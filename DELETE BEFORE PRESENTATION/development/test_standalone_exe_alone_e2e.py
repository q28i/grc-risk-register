"""
Critical End-to-End Test: Standalone EXE Alone in Empty Directory
================================================================
Validates the complete user experience where an empty folder contains ONLY
Start GRC Risk Register.exe.

Verifies:
1. Pure Standalone Bootstrapper in Empty Directory (Zero Python in PATH)
2. Automated Download of GRC-Risk-Register-Payload.zip
3. Automated Provisioning & Verification of Python Runtime
4. Installation into stable %LOCALAPPDATA%\\GRC Risk Register\\
5. Preserved Configured Presentation SQLite Database (3 users, 29 controls, 10 assets, 11 risks)
6. Detached Server Startup & HTTP 200 Readiness
7. Role-Based Access Control & Demo 403 Mutation Guard
8. Absence of DELETE BEFORE PRESENTATION, updater, git-cleanup, Launcher.cs, .git
9. Second Launch Fast-Path (Zero re-download)
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

    install_root = os.path.join(os.environ.get("LOCALAPPDATA", ""), "GRC Risk Register")
    print(f"[Setup] Target stable installation path: {install_root}")

    # Clean prior %LOCALAPPDATA% installation to simulate a genuinely 100% fresh machine
    if os.path.exists(install_root):
        try:
            shutil.rmtree(install_root, ignore_errors=True)
            print(f"[Setup] Cleaned prior %LOCALAPPDATA% installation at {install_root}")
        except Exception as e:
            print(f"[Warning] Could not clean prior installation: {e}")

    # Create empty sandbox directory (simulating Downloads or Desktop folder)
    sandbox = tempfile.mkdtemp(prefix="grc_user_empty_sandbox_")
    print(f"[Sandbox] Empty user folder created at: {sandbox}")

    try:
        kill_port_8000()

        # Step 1: Copy ONLY Start GRC Risk Register.exe into empty sandbox
        sandbox_exe = os.path.join(sandbox, "Start GRC Risk Register.exe")
        shutil.copy2(exe_src, sandbox_exe)
        print(f"  Placed ONLY {os.path.basename(sandbox_exe)} ({os.path.getsize(sandbox_exe):,} bytes) in empty sandbox.")
        assert len(os.listdir(sandbox)) == 1, "Sandbox must contain ONLY Start GRC Risk Register.exe!"

        # Step 2: First Launch (Zero Python in PATH)
        clean_env = clean_environment_path()

        def step_first_launch():
            print("  Running Start GRC Risk Register.exe (Zero Python in PATH)...", flush=True)
            proc = subprocess.Popen([sandbox_exe], cwd=sandbox, env=clean_env)
            proc.wait(timeout=75)
            assert proc.returncode == 0, f"Launcher exited with error code {proc.returncode}"
            print("  Launcher completed setup and exited with code 0.", flush=True)

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

        run_step("1. First Launch: Standalone EXE bootstrap (Payload download + Python runtime + Detached server)", step_first_launch)

        # Step 3: Verify Installation Directory Structure & Absence of Dev Tooling
        def step_verify_install_layout():
            print(f"  Inspecting installed structure in: {install_root}")
            assert os.path.exists(install_root), "%LOCALAPPDATA%\\GRC Risk Register directory missing!"

            app_installed = os.path.join(install_root, "app")
            runtime_installed = os.path.join(install_root, "runtime")
            logs_installed = os.path.join(install_root, "logs")

            assert os.path.exists(app_installed), "app/ folder missing in install directory!"
            assert os.path.exists(runtime_installed), "runtime/ folder missing in install directory!"
            assert os.path.exists(logs_installed), "logs/ folder missing in install directory!"

            # Check runtime executable
            py_exe = os.path.join(runtime_installed, "python.exe")
            assert os.path.exists(py_exe), f"runtime/python.exe missing at {py_exe}!"
            ver_res = subprocess.run([py_exe, "--version"], capture_output=True, text=True, cwd=runtime_installed)
            ver_str = ver_res.stdout.strip() if ver_res.stdout else ver_res.stderr.strip()
            print(f"  Runtime Python execution test: {ver_str}", flush=True)
            assert "Python 3." in ver_str, f"Unexpected version: {ver_str}"

            # Check app.py and database
            assert os.path.exists(os.path.join(app_installed, "app.py")), "app.py missing in app/ folder!"
            db_path = os.path.join(app_installed, "grc_risk_register.db")
            assert os.path.exists(db_path), "grc_risk_register.db missing in app/ folder!"

            # Verify database contents (Preserved presentation state)
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            u_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            fc_count = c.execute("SELECT COUNT(*) FROM feature_controls").fetchone()[0]
            a_count = c.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
            r_count = c.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
            conn.close()
            print(f"  Installed Database: {u_count} users, {fc_count} controls, {a_count} assets, {r_count} risks.")
            assert u_count >= 3, "Users missing in installed DB!"
            assert fc_count >= 29, "Feature controls missing in installed DB!"
            assert a_count >= 10, "Assets missing in installed DB!"
            assert r_count >= 11, "Risks missing in installed DB!"

            # Strict Purity: Check NO development artifacts in installed app
            app_files = os.listdir(app_installed)
            forbidden_in_app = [
                "DELETE BEFORE PRESENTATION", "updater", "git-cleanup", "development",
                "release", ".git", "Launcher.cs", "README_ADMIN.md", "Start GRC Risk Register.exe",
                "Start GRC Risk Register.bat"
            ]
            for item in forbidden_in_app:
                assert item not in app_files, f"Forbidden item '{item}' found in installed app/ folder!"

            print("  Structure audit PASSED (Pristine application installation with zero dev tooling).", flush=True)

        run_step("2. Verify Installation Directory Layout & Clean Payload Purity", step_verify_install_layout)

        # Step 4: Verify Application Functionality on Live Bootstrapped Server
        def step_verify_app_functionality():
            # Admin Login
            p_admin = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=p_admin, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                admin_token = json.loads(resp.read().decode("utf-8"))["token"]

            # Demo Login
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

        run_step("3. Verify RBAC, preserved presentation state, and Demo 403 guards", step_verify_app_functionality)

        # Step 5: Second Launch Fast-Path (Zero re-download)
        def step_second_launch():
            print("  Re-running Start GRC Risk Register.exe in sandbox...", flush=True)
            start_t = time.time()
            proc = subprocess.Popen([sandbox_exe], cwd=sandbox, env=clean_env)
            proc.wait(timeout=5)
            elapsed = time.time() - start_t
            assert proc.returncode == 0, f"Second launch failed with code {proc.returncode}"
            assert elapsed < 5.0, "Second launch took unexpectedly long!"
            print(f"  Second launch instant in {elapsed:.2f}s (fast-path, zero re-download).", flush=True)

        run_step("4. Second Launch Fast-Path (Instant, zero re-download)", step_second_launch)

        print("\n=======================================================")
        print("  CRITICAL STANDALONE EXE E2E CHECKS PASSED (100%)")
        print("=======================================================\n")

    finally:
        kill_port_8000()
        shutil.rmtree(sandbox, ignore_errors=True)

if __name__ == "__main__":
    main()
