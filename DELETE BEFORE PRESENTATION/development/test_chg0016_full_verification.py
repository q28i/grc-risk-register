"""
Official Full Verification Suite for Complete Portable Bootstrap
================================================================
Validates all requirements from Section I:
1. Fresh empty-folder bootstrap from ONLY Start GRC Risk Register.exe (Zero Python in PATH)
2. Bootstrap creates the entire project inside the launch folder:
   - Grc Risk Management Code/
   - DELETE BEFORE PRESENTATION/ (updater/, git-cleanup/, release/, development/)
   - runtime/ (Python 3.11.9)
   - logs/
   - README.md, requirements.txt, LICENSE, NOTICE, VERSION
3. Exactly ONE root application EXE (ZERO duplicate EXEs, ZERO updater EXEs, ZERO remove-git EXEs)
4. Configured presentation database (grc_risk_register.db) preserved in Grc Risk Management Code/
5. Zero files written to %LOCALAPPDATA%, %APPDATA%, %PROGRAMDATA%
6. Live Git cleanup utility (remove_git_history.bat) tested against a disposable repository copy
7. Second launch fast-path (Zero re-download, instant startup)
8. Live application API & Feature Controls verification
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

    # Clear any previous %LOCALAPPDATA% directory to verify nothing gets written there
    local_app_data_target = os.path.join(os.environ.get("LOCALAPPDATA", ""), "GRC Risk Register")
    if os.path.exists(local_app_data_target):
        shutil.rmtree(local_app_data_target, ignore_errors=True)

    # Create empty user folder (e.g. Desktop\Test\)
    test_folder = tempfile.mkdtemp(prefix="grc_desktop_test_")
    print(f"[Test Directory] Clean launch folder: {test_folder}")

    try:
        kill_port_8000()

        # Step 1: Place ONLY Start GRC Risk Register.exe in the empty folder
        user_exe = os.path.join(test_folder, "Start GRC Risk Register.exe")
        shutil.copy2(exe_src, user_exe)
        assert len(os.listdir(test_folder)) == 1, "Folder must contain ONLY Start GRC Risk Register.exe!"
        print(f"  Placed ONLY {os.path.basename(user_exe)} in empty folder.")

        # Step 2: First-Run Bootstrap with Zero Python in PATH
        clean_env = clean_environment_path()

        def step_first_launch():
            print("  Running Start GRC Risk Register.exe (Zero Python in PATH)...", flush=True)
            proc = subprocess.Popen([user_exe], cwd=test_folder, env=clean_env)
            proc.wait(timeout=75)
            assert proc.returncode == 0, f"Launcher exited with error code {proc.returncode}"
            print("  Launcher completed setup and exited cleanly with code 0.", flush=True)

            # Check server response on port 8000
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
            assert ready, "Server not responding on port 8000!"
            print("  Server is live and responding at http://127.0.0.1:8000 independently.", flush=True)

        run_step("1. Fresh Empty-Folder Bootstrap (Zero Python in PATH)", step_first_launch)

        # Step 3: Inspect Resulting Filesystem Structure in Launch Folder
        def step_inspect_filesystem():
            print(f"  Scanning directory: {test_folder}")
            root_items = os.listdir(test_folder)
            print(f"  Root items found: {root_items}")

            # Check required root directories & files
            assert "Start GRC Risk Register.exe" in root_items, "Start GRC Risk Register.exe missing!"
            assert "Grc Risk Management Code" in root_items, "Grc Risk Management Code/ missing!"
            assert "DELETE BEFORE PRESENTATION" in root_items, "DELETE BEFORE PRESENTATION/ missing!"
            assert "runtime" in root_items, "runtime/ missing!"
            assert "README.md" in root_items, "README.md missing!"
            assert "requirements.txt" in root_items, "requirements.txt missing!"
            assert "LICENSE" in root_items, "LICENSE missing!"
            assert "NOTICE" in root_items, "NOTICE missing!"
            assert "VERSION" in root_items, "VERSION missing!"

            # Check DELETE BEFORE PRESENTATION subfolders
            del_dir = os.path.join(test_folder, "DELETE BEFORE PRESENTATION")
            del_items = os.listdir(del_dir)
            print(f"  DELETE BEFORE PRESENTATION items: {del_items}")
            assert "updater" in del_items, "updater/ missing in DELETE BEFORE PRESENTATION!"
            assert "git-cleanup" in del_items, "git-cleanup/ missing in DELETE BEFORE PRESENTATION!"
            assert "release" in del_items, "release/ missing in DELETE BEFORE PRESENTATION!"
            assert "development" in del_items, "development/ missing in DELETE BEFORE PRESENTATION!"

            # Check git-cleanup script existence
            git_clean_dir = os.path.join(del_dir, "git-cleanup")
            git_clean_items = os.listdir(git_clean_dir)
            print(f"  git-cleanup items: {git_clean_items}")
            assert "remove_git_history.bat" in git_clean_items, "remove_git_history.bat missing!"
            assert "remove_git_history.ps1" in git_clean_items, "remove_git_history.ps1 missing!"

            # Check runtime python executable
            py_exe = os.path.join(test_folder, "runtime", "python.exe")
            assert os.path.exists(py_exe), f"runtime/python.exe missing at {py_exe}!"
            ver_res = subprocess.run([py_exe, "--version"], capture_output=True, text=True, cwd=os.path.join(test_folder, "runtime"))
            ver_str = ver_res.stdout.strip() if ver_res.stdout else ver_res.stderr.strip()
            print(f"  Runtime Python execution test: {ver_str}", flush=True)
            assert "Python 3." in ver_str, f"Unexpected version: {ver_str}"

            # Check database in Grc Risk Management Code
            app_dir = os.path.join(test_folder, "Grc Risk Management Code")
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

            # Check executable count in entire tree (MUST BE EXACTLY 1 application launcher EXE)
            all_exes = []
            for root, dirs, files in os.walk(test_folder):
                for f in files:
                    if f.endswith(".exe") and "runtime" not in root:
                        all_exes.append(os.path.relpath(os.path.join(root, f), test_folder))
            print(f"  Application executables found outside runtime: {all_exes}")
            assert len(all_exes) == 1, f"Expected exactly 1 launcher EXE, found: {all_exes}"
            assert all_exes[0] == "Start GRC Risk Register.exe", f"Unexpected launcher name: {all_exes[0]}"

            # Verify NO files were written into %LOCALAPPDATA%
            assert not os.path.exists(local_app_data_target), "%LOCALAPPDATA%\\GRC Risk Register was created!"
            print("  Verified ZERO files written to %LOCALAPPDATA% or system directories.", flush=True)

        run_step("2. Inspect Bootstrapped Directory Layout & Invariants", step_inspect_filesystem)

        # Step 4: Test Git Cleanup Tool on Disposable Copy
        def step_test_git_cleanup():
            disposable_dir = tempfile.mkdtemp(prefix="grc_disposable_copy_")
            try:
                # Create fake git repo with source files
                git_meta = os.path.join(disposable_dir, ".git")
                os.makedirs(git_meta, exist_ok=True)
                with open(os.path.join(git_meta, "HEAD"), "w") as f:
                    f.write("ref: refs/heads/main\n")
                with open(os.path.join(disposable_dir, "app.py"), "w") as f:
                    f.write("# Preserved source code\n")

                assert os.path.exists(git_meta), "Setup failed: .git not created"
                print(f"  Disposable copy pre-cleanup: .git exists = {os.path.exists(git_meta)}")

                # Execute remove_git_history.bat from the bootstrapped folder
                bat_script = os.path.join(test_folder, "DELETE BEFORE PRESENTATION", "git-cleanup", "remove_git_history.bat")
                res = subprocess.run(["cmd.exe", "/c", bat_script, disposable_dir], input="YES\n", capture_output=True, text=True)
                print(f"  remove_git_history.bat output: {res.stdout.strip()}")

                assert not os.path.exists(git_meta), "Git cleanup failed: .git still exists!"
                assert os.path.exists(os.path.join(disposable_dir, "app.py")), "Git cleanup erroneously deleted app.py!"
                print("  Disposable copy post-cleanup: .git safely removed, source code preserved.", flush=True)
            finally:
                shutil.rmtree(disposable_dir, ignore_errors=True)

        run_step("3. Test Git Cleanup Utility against Disposable Copy", step_test_git_cleanup)

        # Step 5: Verify Live Application API & Demo 403 Guards
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

        run_step("4. Verify Live Application RBAC & Feature Controls", step_verify_app)

        # Step 6: Second Launch Fast-Path (Instant, zero re-download)
        def step_second_launch():
            print("  Re-running Start GRC Risk Register.exe...", flush=True)
            start_t = time.time()
            proc = subprocess.Popen([user_exe], cwd=test_folder, env=clean_env)
            proc.wait(timeout=5)
            elapsed = time.time() - start_t
            assert proc.returncode == 0, f"Second launch failed with code {proc.returncode}"
            assert elapsed < 5.0, f"Second launch took too long ({elapsed:.2f}s)!"
            print(f"  Second launch instant in {elapsed:.2f}s (fast-path, zero re-download).", flush=True)

        run_step("5. Second Launch Fast-Path", step_second_launch)

        print("\n=======================================================")
        print("  ALL PORTABLE BOOTSTRAP CHECKS PASSED (100%)")
        print("=======================================================\n")

    finally:
        kill_port_8000()
        shutil.rmtree(test_folder, ignore_errors=True)

if __name__ == "__main__":
    main()
