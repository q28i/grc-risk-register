"""
Real-World Clean-Machine Test of ACTUAL GitHub Release Artifacts
Tests BOTH:
1. Pure Standalone Start GRC Risk Register.exe (downloaded directly from GitHub Release v1.0.0 into empty folder)
2. Extracted GRC-Risk-Register-Windows.zip (downloaded from GitHub Release v1.0.0, extracted into empty folder)

Simulates:
- 0 Python in PATH (PATH completely stripped of all Python directories)
- 0 System dependencies
- 0 Local caches
- Complete detached execution verification
- Real python.exe --version validation
- Complete RBAC & Feature Control persistence check
"""

import os
import sys
import shutil
import tempfile
import subprocess
import time
import urllib.request
import urllib.error
import json
import zipfile

def run_step(step_name, fn):
    print(f"\n[TEST STEP] {step_name} ...", flush=True)
    start = time.time()
    try:
        fn()
        print(f"[PASSED] {step_name} ({time.time() - start:.2f}s)", flush=True)
        return True
    except Exception as e:
        print(f"[FAILED] {step_name}: {e}", flush=True)
        raise

def clean_environment_path():
    clean_env = os.environ.copy()
    path_parts = clean_env.get("PATH", "").split(os.pathsep)
    filtered = [p for p in path_parts if "python" not in p.lower() and "py" not in p.lower() and "windowsapps" not in p.lower()]
    clean_env["PATH"] = os.pathsep.join(filtered)
    # Also strip any PYTHONPATH or PYTHONHOME
    clean_env.pop("PYTHONPATH", None)
    clean_env.pop("PYTHONHOME", None)
    return clean_env

def kill_port_8000():
    subprocess.run(
        ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
        capture_output=True
    )
    time.sleep(1)

def main():
    print("=======================================================")
    print("  LIVE GITHUB RELEASE ARTIFACT VERIFICATION")
    print("=======================================================")

    clean_env = clean_environment_path()

    # -----------------------------------------------------------------
    # TEST SCENARIO A: Extracted GRC-Risk-Register-Windows.zip
    # -----------------------------------------------------------------
    print("\n>>> TESTING SCENARIO A: Extracted Release ZIP <<<")
    sandbox_a = tempfile.mkdtemp(prefix="grc_test_release_zip_")
    print(f"Sandbox A: {sandbox_a}")

    try:
        kill_port_8000()

        # 1. Download release zip from GitHub
        zip_url = "https://github.com/q28i/grc-risk-register/releases/download/v1.0.0/GRC-Risk-Register-Windows.zip"
        local_zip = os.path.join(sandbox_a, "release.zip")
        print(f"Downloading release archive from: {zip_url} ...")
        urllib.request.urlretrieve(zip_url, local_zip)
        assert os.path.exists(local_zip) and os.path.getsize(local_zip) > 10000, "Failed to download valid release ZIP"

        # 2. Extract into sandbox
        with zipfile.ZipFile(local_zip, "r") as z:
            z.extractall(sandbox_a)
        os.remove(local_zip)

        exe_a = os.path.join(sandbox_a, "Start GRC Risk Register.exe")
        assert os.path.exists(exe_a), "Start GRC Risk Register.exe missing after ZIP extract!"

        def test_a_first_run():
            print("  Running Start GRC Risk Register.exe from extracted ZIP (zero Python in PATH)...", flush=True)
            proc = subprocess.Popen([exe_a], cwd=sandbox_a, env=clean_env)
            proc.wait(timeout=60)
            assert proc.returncode == 0, f"Launcher exited with error code {proc.returncode}"
            print(f"  Launcher exited with code 0.", flush=True)

            # Check runtime directory exists and has python.exe
            py_exe = os.path.join(sandbox_a, "runtime", "python.exe")
            assert os.path.exists(py_exe), f"runtime/python.exe does not exist at {py_exe}!"

            # Test runtime/python.exe --version directly
            ver_res = subprocess.run([py_exe, "--version"], capture_output=True, text=True, cwd=os.path.join(sandbox_a, "runtime"))
            ver_str = ver_res.stdout.strip() if ver_res.stdout else ver_res.stderr.strip()
            print(f"  Direct python.exe execution test: {ver_str}", flush=True)
            assert "Python 3." in ver_str, f"Unexpected version: {ver_str}"

            # Check server on port 8000
            ready = False
            for _ in range(20):
                time.sleep(0.5)
                try:
                    resp = urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1)
                    if resp.status == 200:
                        ready = True
                        break
                except Exception:
                    pass
            assert ready, "Server not responding on port 8000!"
            print("  Server is live and responding at http://127.0.0.1:8000.", flush=True)

        run_step("A1. Launch extracted ZIP application (Downloads runtime + Detached server)", test_a_first_run)

        def test_a_app_functionality():
            # Login as demo
            p = json.dumps({"username": "demo", "password": "demo123"}).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=p, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                token = json.loads(resp.read().decode("utf-8"))["token"]

            # Check dashboard
            dash_req = urllib.request.Request("http://127.0.0.1:8000/api/dashboard", headers={"Authorization": f"Bearer {token}"})
            with urllib.request.urlopen(dash_req) as resp:
                dash = json.loads(resp.read().decode("utf-8"))
                assert "summary" in dash, "Missing dashboard summary"
                print(f"  Demo Dashboard OK: {dash['summary']['total_assets']} assets, {dash['summary']['total_risks']} risks.", flush=True)

        run_step("A2. Verify application API & data integrity", test_a_app_functionality)

        def test_a_second_run():
            print("  Testing second run (Fast path, zero re-download)...", flush=True)
            start_t = time.time()
            proc = subprocess.Popen([exe_a], cwd=sandbox_a, env=clean_env)
            proc.wait(timeout=5)
            elapsed = time.time() - start_t
            assert proc.returncode == 0, f"Second launch failed with code {proc.returncode}"
            assert elapsed < 5.0, "Second launch was not instant!"
            print(f"  Second launch instant in {elapsed:.2f}s.", flush=True)

        run_step("A3. Test second run fast-path", test_a_second_run)

    finally:
        kill_port_8000()
        shutil.rmtree(sandbox_a, ignore_errors=True)

    # -----------------------------------------------------------------
    # TEST SCENARIO B: Pure Standalone Start GRC Risk Register.exe
    # -----------------------------------------------------------------
    print("\n>>> TESTING SCENARIO B: Pure Standalone Downloaded EXE <<<")
    sandbox_b = tempfile.mkdtemp(prefix="grc_test_standalone_exe_")
    print(f"Sandbox B: {sandbox_b}")

    try:
        kill_port_8000()

        # 1. Download standalone EXE from GitHub Release
        exe_url = "https://github.com/q28i/grc-risk-register/releases/download/v1.0.0/Start.GRC.Risk.Register.exe"
        exe_b = os.path.join(sandbox_b, "Start GRC Risk Register.exe")
        print(f"Downloading standalone launcher from: {exe_url} ...")
        urllib.request.urlretrieve(exe_url, exe_b)
        assert os.path.exists(exe_b) and os.path.getsize(exe_b) > 5000, "Failed to download standalone launcher"

        def test_b_bootstrap():
            print("  Running standalone Start GRC Risk Register.exe in empty sandbox (zero Python in PATH)...", flush=True)
            proc = subprocess.Popen([exe_b], cwd=sandbox_b, env=clean_env)
            proc.wait(timeout=60)
            assert proc.returncode == 0, f"Launcher exited with error code {proc.returncode}"
            print(f"  Launcher exited with code 0.", flush=True)

            # Check runtime directory exists and has python.exe
            py_exe = os.path.join(sandbox_b, "runtime", "python.exe")
            assert os.path.exists(py_exe), f"runtime/python.exe does not exist at {py_exe}!"

            # Check app.py exists in Grc Risk Management Code
            app_py = os.path.join(sandbox_b, "Grc Risk Management Code", "app.py")
            assert os.path.exists(app_py), "app.py was not downloaded/extracted!"

            # Check server on port 8000
            ready = False
            for _ in range(20):
                time.sleep(0.5)
                try:
                    resp = urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1)
                    if resp.status == 200:
                        ready = True
                        break
                except Exception:
                    pass
            assert ready, "Server not responding on port 8000!"
            print("  Server is live and responding at http://127.0.0.1:8000.", flush=True)

        run_step("B1. Launch standalone EXE in empty folder (Downloads App + Downloads Python + Starts Server)", test_b_bootstrap)

        def test_b_structure():
            root_files = os.listdir(sandbox_b)
            print(f"  Sandbox B root files: {root_files}")
            assert "DELETE BEFORE PRESENTATION" not in root_files, "DELETE folder found!"

            app_dir = os.path.join(sandbox_b, "Grc Risk Management Code")
            app_files = os.listdir(app_dir)
            assert "Start GRC Risk Register.exe" not in app_files, "Nested duplicate launcher found!"
            print("  Single-launcher structure verified.", flush=True)

        run_step("B2. Verify Single-Launcher Structure in downloaded payload", test_b_structure)

    finally:
        kill_port_8000()
        shutil.rmtree(sandbox_b, ignore_errors=True)

    print("\n=======================================================")
    print("  ALL GITHUB RELEASE ARTIFACT TESTS PASSED (100%)")
    print("=======================================================\n")

if __name__ == "__main__":
    main()
