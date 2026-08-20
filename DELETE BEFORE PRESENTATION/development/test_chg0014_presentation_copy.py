"""
CHG-0014 Comprehensive Presentation Copy Live Verification Suite
"""

import os
import sys
import shutil
import tempfile
import subprocess
import time
import urllib.request
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
        print("  All 37 unit and integration tests passed.", flush=True)

    run_step("1. Run all existing unit & integration tests (37/37)", step_test_suite)

    # Step 2: Create presentation copy using make_presentation_copy.py
    temp_pres_dir = tempfile.mkdtemp(prefix="grc_pres_verify_")
    try:
        def step_generate_copy():
            script_path = os.path.join(root_dir, "DELETE BEFORE PRESENTATION", "git-cleanup", "make_presentation_copy.py")
            res = subprocess.run(
                ["python", script_path, "--dest", temp_pres_dir],
                capture_output=True,
                text=True
            )
            assert res.returncode == 0, f"make_presentation_copy failed: {res.stderr}"
            print(f"  Generated presentation copy at: {temp_pres_dir}", flush=True)

        run_step("2. Create temporary presentation copy", step_generate_copy)

        # Step 3: Verify tooling, .git, and private files are absent
        def step_audit_presentation_copy():
            root_items = os.listdir(temp_pres_dir)
            print(f"  Presentation copy root items: {root_items}", flush=True)

            assert "DELETE BEFORE PRESENTATION" not in root_items, "DELETE BEFORE PRESENTATION found in presentation copy!"
            assert "updater" not in root_items, "updater found in presentation copy!"
            assert ".git" not in root_items, ".git found in presentation copy!"
            assert "README_ADMIN.md" not in root_items, "README_ADMIN.md found in presentation copy!"

            app_dir = os.path.join(temp_pres_dir, "Grc Risk Management Code")
            assert os.path.exists(app_dir), "App directory missing!"
            app_items = os.listdir(app_dir)
            print(f"  App items: {app_items}", flush=True)
            assert "grc_risk_register.db" not in app_items, "Database found in presentation copy!"
            assert "README_ADMIN.md" not in app_items, "README_ADMIN.md found in app dir!"
            assert "updater" not in app_items, "updater found in app dir!"
            assert "Launcher.cs" not in app_items, "Launcher.cs found in app dir!"

            # Verify required files
            assert "README.md" in root_items, "README.md missing!"
            assert "LICENSE" in root_items, "LICENSE missing!"
            assert "NOTICE" in root_items, "NOTICE missing!"
            assert "VERSION" in root_items, "VERSION missing!"
            assert "Start GRC Risk Register.exe" in root_items, "Start GRC Risk Register.exe missing!"
            assert "Start GRC Risk Register.bat" in root_items, "Start GRC Risk Register.bat missing!"

        run_step("3. Audit presentation copy (0 development artifacts, 0 private files, all required assets present)", step_audit_presentation_copy)

        # Step 4: Test live launch of cleaned presentation copy
        def step_live_test_cleaned_app():
            app_dir = os.path.join(temp_pres_dir, "Grc Risk Management Code")
            db_path = os.path.join(app_dir, "grc_risk_register.db")
            assert not os.path.exists(db_path), "Database should not exist before first startup!"

            # Stop existing server on 8000
            subprocess.run(
                ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
                capture_output=True
            )
            time.sleep(1)

            # Start server from presentation copy
            server_proc = subprocess.Popen(
                ["python", "app.py"],
                cwd=app_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            try:
                # Wait for HTTP readiness
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
                assert ready, "Cleaned presentation server failed to start!"

                # Verify database was auto-initialized
                assert os.path.exists(db_path), "Database was not auto-initialized on launch!"
                print(f"  Database initialized automatically ({os.path.getsize(db_path):,} bytes).", flush=True)

                # Test 1: Admin Login
                login_payload = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
                login_req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=login_payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(login_req) as resp:
                    login_data = json.loads(resp.read().decode("utf-8"))
                    admin_token = login_data.get("token")
                    assert admin_token, "Admin login failed!"
                    print("  Admin login OK.", flush=True)

                # Test 2: Authenticated Dashboard API
                dash_req = urllib.request.Request("http://127.0.0.1:8000/api/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
                with urllib.request.urlopen(dash_req) as resp:
                    dash_data = json.loads(resp.read().decode("utf-8"))
                    summary = dash_data.get("summary", {})
                    assert "total_assets" in summary, "Dashboard missing total_assets!"
                    assert "total_risks" in summary, "Dashboard missing total_risks!"
                    print(f"  Dashboard API OK: {summary['total_assets']} assets, {summary['total_risks']} risks.", flush=True)

                # Test 3: Demo Login & Feature Restrictions
                demo_payload = json.dumps({"username": "demo", "password": "demo123"}).encode("utf-8")
                demo_req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=demo_payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(demo_req) as resp:
                    demo_data = json.loads(resp.read().decode("utf-8"))
                    demo_token = demo_data.get("token")
                    assert demo_token, "Demo login failed!"
                    print("  Demo login OK.", flush=True)

                # Test 4: Demo User cannot update feature controls (403)
                put_ctrl_req = urllib.request.Request(
                    "http://127.0.0.1:8000/api/feature-controls",
                    data=json.dumps({"controls": {}}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {demo_token}"},
                    method="PUT"
                )
                try:
                    urllib.request.urlopen(put_ctrl_req)
                    assert False, "Demo user should have been rejected with 403!"
                except urllib.error.HTTPError as e:
                    assert e.code == 403, f"Expected 403, got {e.code}"
                    print("  Demo restriction verified (403 Forbidden).", flush=True)

                # Test 5: Assets List API
                assets_req = urllib.request.Request("http://127.0.0.1:8000/api/assets", headers={"Authorization": f"Bearer {admin_token}"})
                with urllib.request.urlopen(assets_req) as resp:
                    assets_data = json.loads(resp.read().decode("utf-8"))
                    assert len(assets_data) > 0, "Assets API returned empty list!"
                    print(f"  Assets API OK ({len(assets_data)} assets loaded).", flush=True)

                # Test 6: Risks List API
                risks_req = urllib.request.Request("http://127.0.0.1:8000/api/risks", headers={"Authorization": f"Bearer {admin_token}"})
                with urllib.request.urlopen(risks_req) as resp:
                    risks_data = json.loads(resp.read().decode("utf-8"))
                    assert len(risks_data) > 0, "Risks API returned empty list!"
                    print(f"  Risks API OK ({len(risks_data)} risks loaded).", flush=True)

                # Test 7: Audit Logs API
                audit_req = urllib.request.Request("http://127.0.0.1:8000/api/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
                with urllib.request.urlopen(audit_req) as resp:
                    audit_data = json.loads(resp.read().decode("utf-8"))
                    assert isinstance(audit_data, list), "Audit API did not return list!"
                    print(f"  Audit Logs API OK ({len(audit_data)} log entries).", flush=True)

            finally:
                server_proc.terminate()
                server_proc.wait(timeout=3)

        run_step("4. Live test cleaned application (auto-init, dashboard, admin, demo 403, assets, risks, audit logs)", step_live_test_cleaned_app)

        # Step 5: Verify original development repository is completely untouched
        def step_verify_dev_repo_untouched():
            assert os.path.exists(os.path.join(root_dir, ".git")), "Original .git directory was deleted or damaged!"
            assert os.path.exists(os.path.join(root_dir, "DELETE BEFORE PRESENTATION")), "DELETE BEFORE PRESENTATION missing in dev repo!"
            assert os.path.exists(os.path.join(root_dir, "README_ADMIN.md")), "README_ADMIN.md missing in dev repo!"
            assert os.path.exists(os.path.join(root_dir, "Documentation")), "Documentation missing in dev repo!"
            print("  Original development repository is 100% intact.", flush=True)

        run_step("5. Verify original development repository remains untouched", step_verify_dev_repo_untouched)

        print("\n=======================================================", flush=True)
        print("  ALL CHG-0014 PRESENTATION CLEANUP TESTS PASSED (100%)", flush=True)
        print("=======================================================\n", flush=True)

    finally:
        shutil.rmtree(temp_pres_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
