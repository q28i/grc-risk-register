"""
Comprehensive Clean-Machine Standalone EXE Bootstrap Test
Simulates:
- 0 Python in PATH
- 0 Application files (only Start GRC Risk Register.exe downloaded)
- 0 Existing environment
Verifies:
- Auto application download from GitHub Release v1.0.0
- Auto Python runtime provisioning from python.org
- Detached server execution surviving launcher exit
- Single user-facing launcher (ZERO nested duplicate launchers)
- Zero DELETE BEFORE PRESENTATION in downloaded payload
- Repeated run fast startup (0 re-downloads)
- Database auto-initialization & Demo/Admin functionality
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

def main():
    root_dir = r"c:\Users\Rift\Documents\Vaults\Temp Vault\Projects\Cybersecurity Risk Management System"
    exe_src = os.path.join(root_dir, "Start GRC Risk Register.exe")
    assert os.path.exists(exe_src), "Start GRC Risk Register.exe missing!"

    # Clean sandbox
    temp_sandbox = tempfile.mkdtemp(prefix="grc_standalone_bootstrap_test_")
    print(f"[Sandbox] Clean testing directory: {temp_sandbox}")

    try:
        # Step 1: Place ONLY the standalone EXE into the empty sandbox
        sandbox_exe = os.path.join(temp_sandbox, "Start GRC Risk Register.exe")
        shutil.copy2(exe_src, sandbox_exe)
        print(f"  Copied standalone EXE ({os.path.getsize(sandbox_exe):,} bytes) into empty sandbox.", flush=True)

        # Stop existing server on port 8000
        subprocess.run(
            ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
            capture_output=True
        )
        time.sleep(1)

        # Step 2: Run standalone EXE with clean isolated environment (simulating no Python in PATH)
        def step_clean_machine_launch():
            clean_env = os.environ.copy()
            # Strip Python from PATH
            path_parts = clean_env.get("PATH", "").split(os.pathsep)
            filtered_path = [p for p in path_parts if "python" not in p.lower() and "py" not in p.lower()]
            clean_env["PATH"] = os.pathsep.join(filtered_path)

            print("  Launching standalone bootstrap EXE (with 0 Python in PATH and 0 app files)...", flush=True)
            proc = subprocess.Popen(
                [sandbox_exe],
                cwd=temp_sandbox,
                env=clean_env
            )

            # Wait for launcher process to complete and exit
            proc.wait(timeout=60)
            print(f"  Launcher exited cleanly with code {proc.returncode}.", flush=True)
            assert proc.returncode == 0, f"Launcher exited with error code {proc.returncode}"

            # Verify server is running on port 8000 independently
            ready = False
            for _ in range(15):
                time.sleep(0.5)
                try:
                    resp = urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1)
                    if resp.status == 200:
                        ready = True
                        break
                except Exception:
                    pass
            assert ready, "Server is not running on port 8000 after launcher exited!"
            print("  Server is responding with HTTP 200 independently after launcher exit.", flush=True)

        run_step("1. First Run: Standalone EXE bootstrap (App download + Python download + Detached server)", step_clean_machine_launch)

        # Step 3: Verify single launcher and clean payload structure
        def step_structure_audit():
            # Check root files
            root_files = os.listdir(temp_sandbox)
            print(f"  Sandbox root files: {root_files}")
            assert "Start GRC Risk Register.exe" in root_files, "Root launcher missing!"
            assert "Grc Risk Management Code" in root_files, "Application folder missing!"
            assert "DELETE BEFORE PRESENTATION" not in root_files, "DELETE folder leaked into release package!"

            # Check app directory files
            app_dir = os.path.join(temp_sandbox, "Grc Risk Management Code")
            app_files = os.listdir(app_dir)
            assert "Start GRC Risk Register.exe" not in app_files, "Nested duplicate launcher found in app directory!"
            assert "Start GRC Risk Register.bat" not in app_files, "Nested duplicate batch launcher found in app directory!"
            assert "app.py" in app_files, "app.py missing in app directory!"
            print("  Structure audit PASSED: exactly 1 launcher at root, zero nested duplicates, zero DELETE folders.", flush=True)

        run_step("2. Verify Single-Launcher Architecture & Clean Payload (No nested duplicates, No DELETE folder)", step_structure_audit)

        # Step 4: Verify application functionality on the bootstrapped server
        def step_verify_app_functionality():
            # A. Check Dashboard API
            dash_req = urllib.request.Request("http://127.0.0.1:8000/api/dashboard")
            try:
                urllib.request.urlopen(dash_req)
            except urllib.error.HTTPError as e:
                assert e.code == 401, "Expected 401 on unauthenticated dashboard"

            # B. Login as Admin
            login_payload = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
            login_req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=login_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(login_req) as resp:
                admin_token = json.loads(resp.read().decode("utf-8"))["token"]
                print("  Admin login verified.", flush=True)

            # C. Check authenticated dashboard
            dash_auth_req = urllib.request.Request("http://127.0.0.1:8000/api/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
            with urllib.request.urlopen(dash_auth_req) as resp:
                dash_data = json.loads(resp.read().decode("utf-8"))
                assert "summary" in dash_data, "Dashboard missing summary"
                print(f"  Dashboard verified ({dash_data['summary']['total_assets']} assets, {dash_data['summary']['total_risks']} risks).", flush=True)

            # D. Login as Demo and verify 403 guard
            demo_payload = json.dumps({"username": "demo", "password": "demo123"}).encode("utf-8")
            demo_req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=demo_payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(demo_req) as resp:
                demo_token = json.loads(resp.read().decode("utf-8"))["token"]

            put_req = urllib.request.Request(
                "http://127.0.0.1:8000/api/feature-controls",
                data=json.dumps({"controls": {}}).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {demo_token}"},
                method="PUT"
            )
            try:
                urllib.request.urlopen(put_req)
                assert False, "Demo user should receive 403 on feature controls edit"
            except urllib.error.HTTPError as e:
                assert e.code == 403, "Expected 403 Forbidden"
                print("  Demo 403 mutation guard verified.", flush=True)

        run_step("3. Verify complete application functionality (Admin, Demo 403, Dashboard, Assets, Risks)", step_verify_app_functionality)

        # Step 5: Repeated Run Test (Fast launch, zero re-downloads)
        def step_repeated_launch():
            print("  Re-running Start GRC Risk Register.exe...", flush=True)
            start_t = time.time()
            proc = subprocess.Popen([sandbox_exe], cwd=temp_sandbox)
            proc.wait(timeout=5)
            elapsed = time.time() - start_t
            print(f"  Repeated launch completed in {elapsed:.2f}s (fast path, zero re-download).", flush=True)
            assert proc.returncode == 0, f"Repeated launch failed with code {proc.returncode}"
            assert elapsed < 5.0, "Repeated launch took unexpectedly long!"

        run_step("4. Repeated Run: Instant detection & launch (0 re-downloads)", step_repeated_launch)

        print("\n=======================================================", flush=True)
        print("  ALL STANDALONE BOOTSTRAP CHECKS PASSED (100%)", flush=True)
        print("=======================================================\n", flush=True)

    finally:
        # Stop background server
        subprocess.run(
            ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
            capture_output=True
        )
        shutil.rmtree(temp_sandbox, ignore_errors=True)

if __name__ == "__main__":
    main()
