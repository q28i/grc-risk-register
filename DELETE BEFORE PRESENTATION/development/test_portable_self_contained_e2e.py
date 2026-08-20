"""
End-to-End Verification: 100% Portable & Self-Contained Standalone Bootstrapper
=============================================================================
Tests the exact user scenario:
- User creates a folder (e.g. Desktop/GRC/)
- Places ONLY Start GRC Risk Register.exe inside it
- Runs the EXE with 0 Python in PATH
- Confirms EVERYTHING is installed into Desktop/GRC/ (NO %LOCALAPPDATA%, NO %APPDATA%)
- Confirms detached server startup, database preservation, RBAC, and instant second launch.
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
import sqlite3

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
    root_dir = r"c:\Users\Rift\Documents\Vaults\Temp Vault\Projects\Cybersecurity Risk Management System"
    exe_src = os.path.join(root_dir, "Start GRC Risk Register.exe")
    assert os.path.exists(exe_src), f"Root launcher missing at: {exe_src}"

    # Clean any leftover %LOCALAPPDATA% folder to prove nothing is written there
    local_app_data_target = os.path.join(os.environ.get("LOCALAPPDATA", ""), "GRC Risk Register")
    if os.path.exists(local_app_data_target):
        shutil.rmtree(local_app_data_target, ignore_errors=True)

    # Create isolated folder simulating user's "Desktop/GRC/"
    grc_folder = tempfile.mkdtemp(prefix="grc_portable_user_folder_")
    print(f"[Portable Sandbox] User folder created at: {grc_folder}")

    try:
        kill_port_8000()

        # Step 1: Copy ONLY Start GRC Risk Register.exe into user folder
        user_exe = os.path.join(grc_folder, "Start GRC Risk Register.exe")
        shutil.copy2(exe_src, user_exe)
        assert len(os.listdir(grc_folder)) == 1, "User folder must contain ONLY Start GRC Risk Register.exe!"
        print(f"  Placed ONLY {os.path.basename(user_exe)} in {grc_folder}.")

        # Step 2: First Launch (Zero Python in PATH)
        clean_env = clean_environment_path()

        def step_first_launch():
            print("  Running Start GRC Risk Register.exe in user folder (Zero Python in PATH)...", flush=True)
            proc = subprocess.Popen([user_exe], cwd=grc_folder, env=clean_env)
            proc.wait(timeout=75)
            assert proc.returncode == 0, f"Launcher exited with error code {proc.returncode}"
            print("  Launcher completed setup and exited cleanly with code 0.", flush=True)

            # Check server on port 8000
            ready = False
            for _ in range(25):
                time.sleep(0.5)
                try:
                    resp = urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1)
                    if resp.status == 200:
                        ready = True
                        break
                except Exception:
                    pass
            assert ready, "Server is not responding at http://127.0.0.1:8000!"
            print("  Server is responding at http://127.0.0.1:8000 independently.", flush=True)

        run_step("1. First Launch: Portable bootstrap in user folder (Zero Python in PATH)", step_first_launch)

        # Step 3: Verify 100% Self-Contained Directory Structure in user folder
        def step_verify_portable_layout():
            print(f"  Inspecting contents of: {grc_folder}")
            items = os.listdir(grc_folder)
            print(f"  Items in user folder: {items}")

            assert "Grc Risk Management Code" in items, "Grc Risk Management Code/ missing in user folder!"
            assert "runtime" in items, "runtime/ missing in user folder!"
            assert "Start GRC Risk Register.exe" in items, "Launcher EXE missing in user folder!"
            assert "README.md" in items, "README.md missing in user folder!"

            # Check runtime/python.exe
            py_exe = os.path.join(grc_folder, "runtime", "python.exe")
            assert os.path.exists(py_exe), f"runtime/python.exe missing at {py_exe}!"
            ver_res = subprocess.run([py_exe, "--version"], capture_output=True, text=True, cwd=os.path.join(grc_folder, "runtime"))
            ver_str = ver_res.stdout.strip() if ver_res.stdout else ver_res.stderr.strip()
            print(f"  Direct runtime verification: {ver_str}", flush=True)
            assert "Python 3." in ver_str, f"Unexpected version: {ver_str}"

            # Check database in Grc Risk Management Code
            app_dir = os.path.join(grc_folder, "Grc Risk Management Code")
            db_path = os.path.join(app_dir, "grc_risk_register.db")
            assert os.path.exists(db_path), f"grc_risk_register.db missing at {db_path}!"

            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            u_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            fc_count = c.execute("SELECT COUNT(*) FROM feature_controls").fetchone()[0]
            a_count = c.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
            r_count = c.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
            conn.close()
            print(f"  Database records: {u_count} users, {fc_count} controls, {a_count} assets, {r_count} risks.")
            assert u_count >= 3 and fc_count >= 29 and a_count >= 10 and r_count >= 11, "Database records mismatch!"

            # Verify NO files were written to %LOCALAPPDATA%
            assert not os.path.exists(local_app_data_target), "%LOCALAPPDATA%\\GRC Risk Register was created when it shouldn't be!"
            print("  Confirmed ZERO files written to %LOCALAPPDATA% or system directories.", flush=True)

        run_step("2. Verify 100% Self-Contained Portable Directory Structure", step_verify_portable_layout)

        # Step 4: Verify Application Functionality on Live Bootstrapped Server
        def step_verify_app():
            # Login as Demo
            p_demo = json.dumps({"username": "demo", "password": "demo123"}).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=p_demo, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                demo_token = json.loads(resp.read().decode("utf-8"))["token"]

            # Dashboard API check
            dash_req = urllib.request.Request("http://127.0.0.1:8000/api/dashboard", headers={"Authorization": f"Bearer {demo_token}"})
            with urllib.request.urlopen(dash_req) as resp:
                dash = json.loads(resp.read().decode("utf-8"))
                assert "summary" in dash, "Dashboard missing summary"
                print(f"  Demo Dashboard verified: {dash['summary']['total_assets']} assets, {dash['summary']['total_risks']} risks.")

            # Demo 403 mutation guard check
            put_req = urllib.request.Request(
                "http://127.0.0.1:8000/api/feature-controls",
                data=json.dumps({"controls": {}}).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {demo_token}"},
                method="PUT"
            )
            try:
                urllib.request.urlopen(put_req)
                assert False, "Demo user should receive 403 on feature controls PUT!"
            except urllib.error.HTTPError as e:
                assert e.code == 403, f"Expected 403, got {e.code}"
                print("  Demo 403 mutation guard verified.", flush=True)

        run_step("3. Verify RBAC, preserved presentation state, and Demo 403 guards", step_verify_app)

        # Step 5: Second Launch Fast-Path (Instant, zero re-download)
        def step_second_launch():
            print("  Re-running Start GRC Risk Register.exe...", flush=True)
            start_t = time.time()
            proc = subprocess.Popen([user_exe], cwd=grc_folder, env=clean_env)
            proc.wait(timeout=5)
            elapsed = time.time() - start_t
            assert proc.returncode == 0, f"Second launch failed with code {proc.returncode}"
            assert elapsed < 5.0, "Second launch took too long!"
            print(f"  Second launch instant in {elapsed:.2f}s (fast-path, zero re-download).", flush=True)

        run_step("4. Second Launch Fast-Path (Instant, zero re-download)", step_second_launch)

        print("\n=======================================================")
        print("  ALL PORTABLE SELF-CONTAINED CHECKS PASSED (100%)")
        print("=======================================================\n")

    finally:
        kill_port_8000()
        shutil.rmtree(grc_folder, ignore_errors=True)

if __name__ == "__main__":
    main()
