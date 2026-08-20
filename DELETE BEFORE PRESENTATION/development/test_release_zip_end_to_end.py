"""
Comprehensive End-to-End Test for the Official Release Package
==============================================================
Validates:
1. Programmatic ZIP Structure (Exactly 1 EXE, canonical name, configured DB present, zero dev tooling)
2. Fresh Extraction in Empty Directory
3. Clean-Machine Startup (Zero Python in PATH)
4. Runtime Provisioning & Python Verification
5. Detached Server Persistence
6. RBAC & Feature Controls Enforcement on Seeded Data
7. Instant Second Launch (Fast-path, zero re-download)
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
    zip_path = os.path.join(root_dir, "GRC-Risk-Register-Windows.zip")
    assert os.path.exists(zip_path), f"Release ZIP not found at: {zip_path}"

    print("=======================================================")
    print("  END-TO-END RELEASE PACKAGE VALIDATION")
    print(f"  Target: {zip_path} ({os.path.getsize(zip_path):,} bytes)")
    print("=======================================================")

    # Step 1: Programmatic ZIP Inspection
    def step_zip_inspection():
        with zipfile.ZipFile(zip_path, "r") as z:
            entries = z.namelist()
            print(f"  Entries in ZIP: {len(entries)}")

            # Executables
            exes = [e for e in entries if e.endswith(".exe")]
            print(f"  Found executables: {exes}")
            assert len(exes) == 1, f"Expected exactly 1 EXE, found {len(exes)}: {exes}"
            assert exes[0] == "Start GRC Risk Register.exe", f"Unexpected EXE name: {exes[0]}"

            # Batch files
            bats = [e for e in entries if e.endswith(".bat")]
            print(f"  Found batch files: {bats}")
            assert len(bats) == 1, f"Expected exactly 1 BAT, found {len(bats)}: {bats}"
            assert bats[0] == "Start GRC Risk Register.bat", f"Unexpected BAT name: {bats[0]}"

            # Invariants
            forbidden = [
                "Start.GRC.Risk.Register.exe", "Launcher.exe", "Launcher.cs",
                "DELETE BEFORE PRESENTATION", ".git", "README_ADMIN.md",
                "updater", "git-cleanup", "development", "release", ".pdf", ".pptx"
            ]
            for e in entries:
                for f in forbidden:
                    assert f not in e, f"Forbidden item '{f}' found in entry '{e}'"

            # Required files
            assert "Grc Risk Management Code/grc_risk_register.db" in entries, "Configured DB missing in ZIP!"
            assert "Grc Risk Management Code/app.py" in entries, "app.py missing in ZIP!"
            assert "README.md" in entries, "README.md missing in ZIP!"
            assert "VERSION" in entries, "VERSION missing in ZIP!"

    run_step("1. Programmatic ZIP structure & invariants validation", step_zip_inspection)

    # Clean sandbox for real execution
    sandbox = tempfile.mkdtemp(prefix="grc_e2e_release_test_")
    print(f"\n[Sandbox] Isolated test directory: {sandbox}")

    try:
        kill_port_8000()

        # Step 2: Extract ZIP into sandbox
        def step_extract():
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(sandbox)
            print(f"  Extracted release package into: {sandbox}")

            # Verify directory structure
            root_items = os.listdir(sandbox)
            print(f"  Extracted root items: {root_items}")
            assert "Start GRC Risk Register.exe" in root_items, "Root launcher missing after extract!"
            assert "Grc Risk Management Code" in root_items, "App directory missing after extract!"
            assert "DELETE BEFORE PRESENTATION" not in root_items, "DELETE folder found in extracted root!"
            assert "Start.GRC.Risk.Register.exe" not in root_items, "Duplicate Start.GRC.Risk.Register.exe found!"

            # Verify no nested launchers in app folder
            app_dir = os.path.join(sandbox, "Grc Risk Management Code")
            app_items = os.listdir(app_dir)
            assert "Start GRC Risk Register.exe" not in app_items, "Nested launcher found in app folder!"
            assert "Start GRC Risk Register.bat" not in app_items, "Nested batch launcher found in app folder!"

            # Verify database records
            db_file = os.path.join(app_dir, "grc_risk_register.db")
            assert os.path.exists(db_file), "grc_risk_register.db missing in app folder!"
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            u_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            fc_count = c.execute("SELECT COUNT(*) FROM feature_controls").fetchone()[0]
            a_count = c.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
            r_count = c.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
            conn.close()
            print(f"  Database records: {u_count} users, {fc_count} controls, {a_count} assets, {r_count} risks.")
            assert u_count >= 3 and fc_count >= 29 and a_count >= 10 and r_count >= 11, "Database records mismatch!"

        run_step("2. Extract ZIP & verify single-launcher clean layout", step_extract)

        # Step 3: Run launcher with zero Python in PATH
        clean_env = clean_environment_path()
        exe_path = os.path.join(sandbox, "Start GRC Risk Register.exe")

        def step_launch_first_run():
            print("  Running Start GRC Risk Register.exe (Zero Python in PATH)...", flush=True)
            proc = subprocess.Popen([exe_path], cwd=sandbox, env=clean_env)
            proc.wait(timeout=60)
            assert proc.returncode == 0, f"Launcher exited with non-zero code {proc.returncode}"
            print(f"  Launcher exited with code 0.", flush=True)

            # Verify runtime/python.exe exists and works
            py_exe = os.path.join(sandbox, "runtime", "python.exe")
            assert os.path.exists(py_exe), f"runtime/python.exe missing at {py_exe}!"

            ver_res = subprocess.run([py_exe, "--version"], capture_output=True, text=True, cwd=os.path.join(sandbox, "runtime"))
            ver_str = ver_res.stdout.strip() if ver_res.stdout else ver_res.stderr.strip()
            print(f"  Live runtime verification: {ver_str}", flush=True)
            assert "Python 3." in ver_str, f"Unexpected version: {ver_str}"

            # Verify server on port 8000
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

        run_step("3. Execute launcher on fresh environment (Runtime provisioning + Detached server)", step_launch_first_run)

        # Step 4: Verify application functionality & preserved configuration
        def step_verify_app():
            # A. Admin Login
            p_admin = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=p_admin, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                admin_token = json.loads(resp.read().decode("utf-8"))["token"]

            # B. Demo Login
            p_demo = json.dumps({"username": "demo", "password": "demo123"}).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=p_demo, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                demo_token = json.loads(resp.read().decode("utf-8"))["token"]

            # C. Check authenticated dashboard
            dash_req = urllib.request.Request("http://127.0.0.1:8000/api/dashboard", headers={"Authorization": f"Bearer {demo_token}"})
            with urllib.request.urlopen(dash_req) as resp:
                dash = json.loads(resp.read().decode("utf-8"))
                assert "summary" in dash, "Missing dashboard summary"
                print(f"  Demo Dashboard: {dash['summary']['total_assets']} assets, {dash['summary']['total_risks']} risks.")
                assert dash["summary"]["total_assets"] >= 10, "Preserved assets missing!"
                assert dash["summary"]["total_risks"] >= 11, "Preserved risks missing!"

            # D. Verify Demo 403 guard on feature controls
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

        run_step("4. Verify application RBAC, preserved data, and Demo permissions", step_verify_app)

        # Step 5: Second Launch Fast-Path
        def step_second_launch():
            print("  Re-running Start GRC Risk Register.exe...", flush=True)
            start_t = time.time()
            proc = subprocess.Popen([exe_path], cwd=sandbox, env=clean_env)
            proc.wait(timeout=5)
            elapsed = time.time() - start_t
            assert proc.returncode == 0, f"Second launch failed with code {proc.returncode}"
            assert elapsed < 5.0, "Second launch took too long!"
            print(f"  Second launch instant in {elapsed:.2f}s (fast path, zero re-download).", flush=True)

        run_step("5. Test second launch fast-path (Instant, zero re-download)", step_second_launch)

        print("\n=======================================================")
        print("  ALL END-TO-END RELEASE VALIDATION CHECKS PASSED (100%)")
        print("=======================================================\n")

    finally:
        kill_port_8000()
        shutil.rmtree(sandbox, ignore_errors=True)

if __name__ == "__main__":
    main()
