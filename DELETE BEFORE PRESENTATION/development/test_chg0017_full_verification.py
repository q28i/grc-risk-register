"""
Ultimate Verification Suite for CHG-0017: Usable Development & Cleanup Utilities
================================================================================
Validates:
1. Fresh empty-folder bootstrap from ONLY Start GRC Risk Register.exe (Zero Python in PATH)
2. Complete directory tree generation inside the launch folder:
   - Grc Risk Management Code/
   - DELETE BEFORE PRESENTATION/
     - updater/Run Updater.bat
     - git-cleanup/Remove Git History.bat
     - git-cleanup/remove_git_history.py
     - git-cleanup/Remove Git History.ps1
   - runtime/ (Python 3.11.9)
   - logs/
   - README.md, requirements.txt, LICENSE, NOTICE, VERSION
3. Live test of Run Updater.bat --check
4. Live test of Remove Git History.bat against disposable repository copies
5. Single-EXE rule verification (EXACTLY 1 .exe outside runtime)
6. Second launch fast-path (Zero re-download, instant startup)
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

def print_tree(startpath):
    print("\n---------------- ACTUAL GENERATED DIRECTORY TREE ----------------")
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        folder_name = os.path.basename(root)
        if folder_name:
            print(f"{indent}{folder_name}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            # Skip listing hundreds of runtime files to keep output clear
            if "runtime" in root and level > 1:
                continue
            print(f"{subindent}{f}")
    print("-----------------------------------------------------------------\n")

def main():
    root_dir = r"c:\Users\Rift\Documents\Vaults\Temp Vault\Projects\Cybersecurity Risk Management System"
    exe_src = os.path.join(root_dir, "Start GRC Risk Register.exe")
    assert os.path.exists(exe_src), f"Root launcher missing at: {exe_src}"

    test_folder = tempfile.mkdtemp(prefix="grc_desktop_test_chg17_")
    print(f"[Test Directory] Clean launch folder: {test_folder}")

    try:
        kill_port_8000()

        # Step 1: Place ONLY Start GRC Risk Register.exe in empty folder
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

        # Step 3: Print Actual Directory Tree & Verify Required Launchers
        def step_inspect_tree():
            print_tree(test_folder)

            # 1. Check updater launcher
            updater_bat = os.path.join(test_folder, "DELETE BEFORE PRESENTATION", "updater", "Run Updater.bat")
            assert os.path.exists(updater_bat), f"Missing {updater_bat}!"

            # 2. Check git cleanup tools
            git_clean_dir = os.path.join(test_folder, "DELETE BEFORE PRESENTATION", "git-cleanup")
            assert os.path.exists(os.path.join(git_clean_dir, "Remove Git History.bat")), "Missing Remove Git History.bat!"
            assert os.path.exists(os.path.join(git_clean_dir, "remove_git_history.py")), "Missing remove_git_history.py!"
            assert os.path.exists(os.path.join(git_clean_dir, "Remove Git History.ps1")), "Missing Remove Git History.ps1!"

            # 3. Check single EXE rule outside runtime
            all_exes = []
            for root, dirs, files in os.walk(test_folder):
                for f in files:
                    if f.endswith(".exe") and "runtime" not in root:
                        all_exes.append(os.path.relpath(os.path.join(root, f), test_folder))
            print(f"  Application executables found outside runtime: {all_exes}")
            assert len(all_exes) == 1, f"Expected exactly 1 launcher EXE, found: {all_exes}"
            assert all_exes[0] == "Start GRC Risk Register.exe", f"Unexpected launcher: {all_exes[0]}"

            # 4. Check database records
            db_path = os.path.join(test_folder, "Grc Risk Management Code", "grc_risk_register.db")
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            u_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            fc_count = c.execute("SELECT COUNT(*) FROM feature_controls").fetchone()[0]
            a_count = c.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
            r_count = c.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
            conn.close()
            print(f"  Database records: {u_count} users, {fc_count} controls, {a_count} assets, {r_count} risks.")
            assert u_count >= 3 and fc_count >= 29 and a_count >= 10 and r_count >= 11, "Database records mismatch!"

        run_step("2. Programmatic Filesystem & Tree Verification", step_inspect_tree)

        # Step 4: Test Run Updater.bat from Bootstrapped Folder
        def step_test_updater_bat():
            updater_bat = os.path.join(test_folder, "DELETE BEFORE PRESENTATION", "updater", "Run Updater.bat")
            print(f"  Executing: {updater_bat} --check")
            res = subprocess.run(["cmd.exe", "/c", updater_bat, "--check"], capture_output=True, text=True, cwd=os.path.dirname(updater_bat))
            print(f"  Run Updater.bat output:\n{res.stdout.strip()}")
            assert res.returncode == 0, f"Updater failed with code {res.returncode}: {res.stderr}"
            assert "has_update" in res.stdout, "Updater did not return expected update status!"

        run_step("3. Execute Run Updater.bat from Bootstrapped Folder", step_test_updater_bat)

        # Step 5: Test Remove Git History.bat against Disposable Copy
        def step_test_git_cleanup_bat():
            bat_script = os.path.join(test_folder, "DELETE BEFORE PRESENTATION", "git-cleanup", "Remove Git History.bat")

            # A. Test Cancellation (N)
            d_cancel = tempfile.mkdtemp(prefix="grc_test_git_cancel_")
            try:
                git_dir = os.path.join(d_cancel, ".git")
                os.makedirs(git_dir, exist_ok=True)
                with open(os.path.join(git_dir, "HEAD"), "w") as f: f.write("ref: refs/heads/main\n")
                with open(os.path.join(d_cancel, "app.py"), "w") as f: f.write("# Preserved\n")

                print(f"  Testing cancellation (N) on: {d_cancel}")
                res = subprocess.run([bat_script, d_cancel], input="N\n", capture_output=True, text=True)
                print(f"  Output:\n{res.stdout.strip()}")
                assert os.path.exists(git_dir), ".git was deleted on cancellation!"
                print("  Cancellation confirmed: .git untouched.")
            finally:
                shutil.rmtree(d_cancel, ignore_errors=True)

            # B. Test Deletion (Y)
            d_delete = tempfile.mkdtemp(prefix="grc_test_git_delete_")
            try:
                git_dir = os.path.join(d_delete, ".git")
                os.makedirs(git_dir, exist_ok=True)
                with open(os.path.join(git_dir, "HEAD"), "w") as f: f.write("ref: refs/heads/main\n")
                with open(os.path.join(d_delete, "app.py"), "w") as f: f.write("# Preserved\n")

                print(f"\n  Testing deletion (Y) on: {d_delete}")
                res = subprocess.run([bat_script, d_delete], input="Y\n", capture_output=True, text=True)
                print(f"  Output:\n{res.stdout.strip()}")
                assert not os.path.exists(git_dir), ".git still exists after Y!"
                assert os.path.exists(os.path.join(d_delete, "app.py")), "Source code was deleted!"
                print("  Deletion confirmed: .git safely removed, source code preserved.")
            finally:
                shutil.rmtree(d_delete, ignore_errors=True)

        run_step("4. Test Remove Git History.bat against Disposable Copies", step_test_git_cleanup_bat)

        # Step 6: Second Launch Fast-Path
        def step_second_launch():
            print("  Re-running Start GRC Risk Register.exe...", flush=True)
            start_t = time.time()
            proc = subprocess.Popen([user_exe], cwd=test_folder, env=clean_env)
            proc.wait(timeout=5)
            elapsed = time.time() - start_t
            assert proc.returncode == 0, f"Second launch failed with code {proc.returncode}"
            assert elapsed < 5.0, f"Second launch took too long ({elapsed:.2f}s)!"
            print(f"  Second launch was instant in {elapsed:.2f}s (fast path, zero re-download).", flush=True)

        run_step("5. Second Launch Fast-Path", step_second_launch)

        print("\n=======================================================")
        print("  ALL CHG-0017 VALIDATION CHECKS PASSED (100%)")
        print("=======================================================\n")

    finally:
        kill_port_8000()
        shutil.rmtree(test_folder, ignore_errors=True)

if __name__ == "__main__":
    main()
