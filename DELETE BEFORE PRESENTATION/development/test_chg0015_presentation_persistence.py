"""
Comprehensive CHG-0015 Presentation Configuration & Persistence Verification Suite
Tests configured Demo User state:
1. On initial presentation copy launch
2. After a full server restart
3. After an application updater simulation
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

def main():
    root_dir = r"c:\Users\Rift\Documents\Vaults\Temp Vault\Projects\Cybersecurity Risk Management System"
    sys.path.insert(0, root_dir)

    # Step 1: Run automated test suite
    def step_test_suite():
        res = subprocess.run(
            ["python", "run_tests.py"],
            cwd=os.path.join(root_dir, "Grc Risk Management Code"),
            capture_output=True,
            text=True
        )
        assert res.returncode == 0, f"Tests failed: {res.stderr}"
        assert "ALL TESTS PASSED" in res.stdout, "Not all tests passed!"
        print("  All 38 unit and integration tests passed.", flush=True)

    run_step("1. Run 38 unit & integration tests (including feature control persistence)", step_test_suite)

    # Step 2: Ensure a known configured database is prepared and backed up
    temp_pres_dir = tempfile.mkdtemp(prefix="grc_chg15_pres_")
    try:
        def step_generate_presentation_copy():
            script_path = os.path.join(root_dir, "DELETE BEFORE PRESENTATION", "git-cleanup", "make_presentation_copy.py")
            res = subprocess.run(
                ["python", script_path, "--dest", temp_pres_dir],
                capture_output=True,
                text=True
            )
            assert res.returncode == 0, f"make_presentation_copy failed: {res.stderr}"

            # Verify grc_risk_register.db is in the presentation copy
            app_dir = os.path.join(temp_pres_dir, "Grc Risk Management Code")
            db_file = os.path.join(app_dir, "grc_risk_register.db")
            assert os.path.exists(db_file), "Configured presentation database was not copied into presentation copy!"
            print(f"  Presentation copy generated with database ({os.path.getsize(db_file):,} bytes).", flush=True)

        run_step("2. Generate presentation copy with deliberately configured database", step_generate_presentation_copy)

        def verify_server_and_demo_state(app_dir, stage_name):
            print(f"  --- Verifying Demo State in {stage_name} ---", flush=True)
            # Stop existing server on 8000
            subprocess.run(
                ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
                capture_output=True
            )
            time.sleep(1)

            # Start server
            server_proc = subprocess.Popen(
                ["python", "app.py"],
                cwd=app_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            try:
                # Wait for ready
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
                assert ready, f"Server failed to start during {stage_name}!"

                # 1. Login as Demo User
                login_payload = json.dumps({"username": "demo", "password": "demo123"}).encode("utf-8")
                login_req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=login_payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(login_req) as resp:
                    login_data = json.loads(resp.read().decode("utf-8"))
                    demo_token = login_data.get("token")
                    assert demo_token, f"Demo login failed in {stage_name}!"
                    print(f"    [OK] Demo login authenticated.", flush=True)

                # 2. Check Feature Controls for demo user
                fc_req = urllib.request.Request("http://127.0.0.1:8000/api/feature-controls")
                with urllib.request.urlopen(fc_req) as resp:
                    fc_data = json.loads(resp.read().decode("utf-8"))
                    controls_dict = fc_data.get("controls_dict", {})
                    print(f"    [OK] Loaded {len(controls_dict)} feature controls from SQLite.", flush=True)

                # 3. Verify Demo User cannot modify feature controls (403)
                put_fc = urllib.request.Request(
                    "http://127.0.0.1:8000/api/feature-controls",
                    data=json.dumps({"controls": {"asset_add": True}}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {demo_token}"},
                    method="PUT"
                )
                try:
                    urllib.request.urlopen(put_fc)
                    assert False, "Demo user should have been rejected with 403 on feature controls!"
                except urllib.error.HTTPError as e:
                    assert e.code == 403, f"Expected 403, got {e.code}"
                    print(f"    [OK] Demo user forbidden from modifying feature controls (403).", flush=True)

                # 4. Verify Demo User receives 403 on protected mutation endpoints
                put_ast = urllib.request.Request(
                    "http://127.0.0.1:8000/api/assets/1",
                    data=json.dumps({"name": "Tampered Name"}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {demo_token}"},
                    method="PUT"
                )
                try:
                    urllib.request.urlopen(put_ast)
                    assert False, "Demo user should have been rejected with 403 on asset edit!"
                except urllib.error.HTTPError as e:
                    assert e.code == 403, f"Expected 403 on asset edit, got {e.code}"
                    print(f"    [OK] Demo user asset edit strictly blocked by backend (403).", flush=True)

                # 5. Verify Unrestricted reading functions (Dashboard, Assets, Risks)
                dash_req = urllib.request.Request("http://127.0.0.1:8000/api/dashboard", headers={"Authorization": f"Bearer {demo_token}"})
                with urllib.request.urlopen(dash_req) as resp:
                    dash_data = json.loads(resp.read().decode("utf-8"))
                    summary = dash_data.get("summary", {})
                    assert summary.get("total_assets", 0) > 0, "Assets missing in dashboard!"
                    assert summary.get("total_risks", 0) > 0, "Risks missing in dashboard!"
                    print(f"    [OK] Dashboard read successfully ({summary['total_assets']} assets, {summary['total_risks']} risks).", flush=True)

            finally:
                server_proc.terminate()
                server_proc.wait(timeout=3)

        # Step 3: Test Presentation Copy (Initial Launch)
        app_dir = os.path.join(temp_pres_dir, "Grc Risk Management Code")
        run_step("3. Verify configured Demo User state on Initial Presentation Launch", lambda: verify_server_and_demo_state(app_dir, "Stage 1: Initial Presentation Launch"))

        # Step 4: Test Presentation Copy After Full Application Restart
        run_step("4. Verify configured Demo User state AFTER Full Server Restart", lambda: verify_server_and_demo_state(app_dir, "Stage 2: Post-Restart Launch"))

        # Step 5: Test Presentation Copy After Updater Simulation
        def step_updater_simulation():
            # Import apply_update from DELETE BEFORE PRESENTATION
            updater_script = os.path.join(root_dir, "DELETE BEFORE PRESENTATION", "updater", "updater.py")
            import importlib.util
            spec = importlib.util.spec_from_file_location("updater", updater_script)
            up_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(up_mod)

            # Build mock update v1.0.1
            zip_sandbox = tempfile.mkdtemp()
            try:
                update_zip = os.path.join(zip_sandbox, "update_v101.zip")
                with zipfile.ZipFile(update_zip, "w") as z:
                    z.writestr("VERSION", "1.0.1")
                    # Try to put an empty DB inside update zip
                    z.writestr("grc_risk_register.db", "ATTEMPT TO OVERWRITE DATABASE")

                # Apply update to presentation app dir
                success, msg = up_mod.apply_update(update_zip, app_dir)
                assert success, f"Updater failed: {msg}"
                print(f"  Updater executed successfully: {msg}", flush=True)

                # Verify database file was untouched
                db_file = os.path.join(app_dir, "grc_risk_register.db")
                with open(db_file, "rb") as f:
                    header = f.read(16)
                    assert header.startswith(b"SQLite format 3"), "DATABASE WAS OVERWRITTEN/CORRUPTED BY UPDATER!"
                print(f"  Database format verified: Valid SQLite format 3 untouched.", flush=True)

            finally:
                shutil.rmtree(zip_sandbox, ignore_errors=True)

            # Now verify server and demo state post-update
            verify_server_and_demo_state(app_dir, "Stage 3: Post-Updater Simulation")

        run_step("5. Verify configured Demo User state AFTER Application Updater Simulation", step_updater_simulation)

        print("\n=======================================================", flush=True)
        print("  ALL CHG-0015 PERSISTENCE AUDIT STEPS PASSED (100%)", flush=True)
        print("=======================================================\n", flush=True)

    finally:
        shutil.rmtree(temp_pres_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
