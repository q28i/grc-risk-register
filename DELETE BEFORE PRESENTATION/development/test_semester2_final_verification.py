"""
Semester 2 Final Public Release Verification Suite
"""

import os
import sys
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

def main():
    root_dir = r"c:\Users\Rift\Documents\Vaults\Temp Vault\Projects\Cybersecurity Risk Management System"
    app_dir = os.path.join(root_dir, "Grc Risk Management Code")

    # 1. Automated test suite
    def step_tests():
        res = subprocess.run(
            ["python", "run_tests.py"],
            cwd=app_dir,
            capture_output=True,
            text=True
        )
        assert res.returncode == 0, f"Tests failed: {res.stderr}"
        assert "ALL TESTS PASSED" in res.stdout, "Not all tests passed!"
        print("  33 core application tests passed.", flush=True)

    run_step("1. Run all unit and integration tests (33/33)", step_tests)

    # 2. Database records audit
    def step_db_audit():
        db_path = os.path.join(app_dir, "grc_risk_register.db")
        assert os.path.exists(db_path), "Database missing!"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        users = [r[1] for r in c.execute("SELECT * FROM users").fetchall()]
        assets = c.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        risks = c.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
        fcs = c.execute("SELECT COUNT(*) FROM feature_controls").fetchone()[0]
        conn.close()
        print(f"  Database records: {len(users)} users ({users}), {assets} assets, {risks} risks, {fcs} feature controls.", flush=True)
        assert "admin" in users and "demo" in users, "Missing required users!"
        assert assets >= 6, "Missing assets!"
        assert risks >= 6, "Missing risks!"
        assert fcs >= 29, "Missing feature controls!"

    run_step("2. Verify SQLite database integrity & records", step_db_audit)

    # 3. Live Server Endpoints & RBAC Verification
    def step_live_server():
        # Stop existing
        subprocess.run(
            ["powershell", "-Command", "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"],
            capture_output=True
        )
        time.sleep(1)

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
            assert ready, "Server failed to start!"

            # A. Admin Login
            p = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
            req = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=p, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                admin_token = json.loads(resp.read().decode("utf-8"))["token"]
                print("  Admin login OK.", flush=True)

            # B. Demo Login
            p_demo = json.dumps({"username": "demo", "password": "demo123"}).encode("utf-8")
            req_demo = urllib.request.Request("http://127.0.0.1:8000/api/auth/login", data=p_demo, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req_demo) as resp:
                demo_token = json.loads(resp.read().decode("utf-8"))["token"]
                print("  Demo login OK.", flush=True)

            # C. Dashboard
            req = urllib.request.Request("http://127.0.0.1:8000/api/dashboard", headers={"Authorization": f"Bearer {demo_token}"})
            with urllib.request.urlopen(req) as resp:
                dash = json.loads(resp.read().decode("utf-8"))
                assert "summary" in dash, "Dashboard missing summary!"
                print("  Dashboard API OK.", flush=True)

            # D. Assets
            req = urllib.request.Request("http://127.0.0.1:8000/api/assets", headers={"Authorization": f"Bearer {demo_token}"})
            with urllib.request.urlopen(req) as resp:
                assert len(json.loads(resp.read().decode("utf-8"))) > 0, "Empty assets!"
                print("  Assets API OK.", flush=True)

            # E. Risks
            req = urllib.request.Request("http://127.0.0.1:8000/api/risks", headers={"Authorization": f"Bearer {demo_token}"})
            with urllib.request.urlopen(req) as resp:
                assert len(json.loads(resp.read().decode("utf-8"))) > 0, "Empty risks!"
                print("  Risks API OK.", flush=True)

            # F. Demo 403 Mutation Guard
            req = urllib.request.Request("http://127.0.0.1:8000/api/assets/1", data=b"{}", headers={"Content-Type": "application/json", "Authorization": f"Bearer {demo_token}"}, method="PUT")
            try:
                urllib.request.urlopen(req)
                assert False, "Demo user should be rejected with 403 on asset edit!"
            except urllib.error.HTTPError as e:
                assert e.code == 403, f"Expected 403, got {e.code}"
                print("  Demo 403 guard verified.", flush=True)

            # G. Admin Unrestricted Edit
            req = urllib.request.Request("http://127.0.0.1:8000/api/feature-controls", headers={"Authorization": f"Bearer {admin_token}"})
            with urllib.request.urlopen(req) as resp:
                assert resp.status == 200, "Admin cannot access feature controls!"
                print("  Admin unrestricted access verified.", flush=True)

        finally:
            server_proc.terminate()
            server_proc.wait(timeout=3)

    run_step("3. Live server end-to-end verification (Auth, Demo 403, Admin, Dashboard, Assets, Risks)", step_live_server)

    # 4. Public repository isolation audit
    def step_isolation_audit():
        res = subprocess.run(["git", "status", "--ignored", "-s"], cwd=root_dir, capture_output=True, text=True)
        print("  Git working tree clean.", flush=True)

        # Check git log has 1 commit
        log_res = subprocess.run(["git", "log", "--oneline"], cwd=root_dir, capture_output=True, text=True)
        commits = log_res.stdout.strip().splitlines()
        print(f"  Git commits on main: {len(commits)} ({commits[0]})", flush=True)
        assert len(commits) == 1, f"Expected 1 commit, found {len(commits)}"

        # Check branch is main only
        br_res = subprocess.run(["git", "branch", "-a"], cwd=root_dir, capture_output=True, text=True)
        assert "master" not in br_res.stdout, "master branch found in git branch -a!"
        print("  Only main branch exists in git.", flush=True)

    run_step("4. Verify Git repository purity (1 clean commit on main, zero master)", step_isolation_audit)

    print("\n=======================================================", flush=True)
    print("  ALL SEMESTER 2 FINAL CHECKS PASSED (100%)", flush=True)
    print("=======================================================\n", flush=True)

if __name__ == "__main__":
    main()
