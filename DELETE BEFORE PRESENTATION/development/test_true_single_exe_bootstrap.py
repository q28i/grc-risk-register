"""
Official Comprehensive Verification Suite: True Single-EXE Bootstrap
====================================================================
Validates all requirements from the distribution architecture redesign:
- TEST A: Fresh Install from empty folder containing ONLY Start GRC Risk Register.exe
- TEST B: Second Launch Fast-Path (Instant, zero re-download)
- TEST C: Payload Purity (Zero dev tooling, zero git, zero duplicate launchers in installed app)
- TEST D: Release Assets Audit (Single official executable on GitHub Releases)
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
    print(f"[Setup] Target installation directory: {install_root}")

    # Clear prior %LOCALAPPDATA% installation to guarantee clean-machine test
    if os.path.exists(install_root):
        try:
            shutil.rmtree(install_root, ignore_errors=True)
            print(f"[Setup] Cleared existing %LOCALAPPDATA% installation.")
        except Exception as e:
            print(f"[Warning] Could not clear install directory: {e}")

    # Create empty sandbox directory
    sandbox = tempfile.mkdtemp(prefix="grc_single_exe_test_")
    print(f"[Sandbox] Created empty sandbox: {sandbox}")

    try:
        kill_port_8000()

        # -------------------------------------------------------------
        # TEST A: COMPLETELY FRESH INSTALL
        # -------------------------------------------------------------
        sandbox_exe = os.path.join(sandbox, "Start GRC Risk Register.exe")
        shutil.copy2(exe_src, sandbox_exe)
        assert len(os.listdir(sandbox)) == 1, "Sandbox must contain ONLY Start GRC Risk Register.exe!"
        print(f"  Placed ONLY {os.path.basename(sandbox_exe)} in empty folder.")

        clean_env = clean_environment_path()

        def test_a_fresh_install():
            print("  Running Start GRC Risk Register.exe (Zero Python in PATH)...", flush=True)
            proc = subprocess.Popen([sandbox_exe], cwd=sandbox, env=clean_env)
            proc.wait(timeout=75)
            assert proc.returncode == 0, f"Launcher exited with error code {proc.returncode}"
            print("  Launcher completed bootstrap and exited cleanly with code 0.", flush=True)

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
            assert ready, "Server not responding on port 8000!"
            print("  Server is live and responding at http://127.0.0.1:8000 independently.", flush=True)

        run_step("TEST A — Completely Fresh Install (Payload download + Python runtime + Detached server)", test_a_fresh_install)

        # -------------------------------------------------------------
        # TEST B: SECOND LAUNCH (Fast-Path, zero re-download)
        # -------------------------------------------------------------
        def test_b_second_launch():
            print("  Re-running Start GRC Risk Register.exe...", flush=True)
            start_t = time.time()
            proc = subprocess.Popen([sandbox_exe], cwd=sandbox, env=clean_env)
            proc.wait(timeout=5)
            elapsed = time.time() - start_t
            assert proc.returncode == 0, f"Second launch failed with code {proc.returncode}"
            assert elapsed < 5.0, f"Second launch took too long ({elapsed:.2f}s)!"
            print(f"  Second launch was instant in {elapsed:.2f}s (fast path, zero re-download).", flush=True)

        run_step("TEST B — Second Launch Fast-Path", test_b_second_launch)

        # -------------------------------------------------------------
        # TEST C: PAYLOAD PURITY & PRESERVED DATABASE
        # -------------------------------------------------------------
        def test_c_payload_purity():
            app_dir = os.path.join(install_root, "app")
            runtime_dir = os.path.join(install_root, "runtime")
            assert os.path.exists(app_dir), "app/ folder missing in install directory!"
            assert os.path.exists(runtime_dir), "runtime/ folder missing in install directory!"

            # Check runtime execution
            py_exe = os.path.join(runtime_dir, "python.exe")
            assert os.path.exists(py_exe), f"python.exe missing at {py_exe}"
            ver_res = subprocess.run([py_exe, "--version"], capture_output=True, text=True, cwd=runtime_dir)
            ver_str = ver_res.stdout.strip() if ver_res.stdout else ver_res.stderr.strip()
            print(f"  Runtime Python version: {ver_str}", flush=True)
            assert "Python 3." in ver_str, f"Unexpected version: {ver_str}"

            # Check database records
            db_path = os.path.join(app_dir, "grc_risk_register.db")
            assert os.path.exists(db_path), "grc_risk_register.db missing in app folder!"
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            u_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            fc_count = c.execute("SELECT COUNT(*) FROM feature_controls").fetchone()[0]
            a_count = c.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
            r_count = c.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
            conn.close()
            print(f"  Installed Database: {u_count} users, {fc_count} controls, {a_count} assets, {r_count} risks.")
            assert u_count >= 3 and fc_count >= 29 and a_count >= 10 and r_count >= 11, "Database records mismatch!"

            # Check zero development tooling in installed app
            app_items = os.listdir(app_dir)
            forbidden = [
                "DELETE BEFORE PRESENTATION", "updater", "git-cleanup", "development",
                "release", ".git", "Launcher.cs", "README_ADMIN.md", "Start GRC Risk Register.exe",
                "Start GRC Risk Register.bat", "tests"
            ]
            for forb in forbidden:
                assert forb not in app_items, f"Forbidden item '{forb}' found in installed app!"

            print("  Installed app purity verified (Zero dev tooling, zero duplicate launchers).", flush=True)

        run_step("TEST C — Payload Purity & Database Preservation", test_c_payload_purity)

        # -------------------------------------------------------------
        # TEST D: GITHUB RELEASE ASSETS AUDIT
        # -------------------------------------------------------------
        def test_d_release_audit():
            gh_res = subprocess.run(
                ["powershell", "-Command", '& "C:\\Users\\Rift\\AppData\\Local\\Programs\\gh\\bin\\gh.exe" release view v1.0.0 --json assets'],
                capture_output=True, text=True
            )
            assert gh_res.returncode == 0, f"Failed to query GitHub release: {gh_res.stderr}"
            data = json.loads(gh_res.stdout)
            asset_names = [a["name"] for a in data.get("assets", [])]
            print(f"  GitHub Release v1.0.0 Assets: {asset_names}", flush=True)

            # Ensure Start GRC Risk Register.exe exists
            assert any("Start" in a and a.endswith(".exe") for a in asset_names), "Standalone launcher missing from release!"
            assert "GRC-Risk-Register-Payload.zip" in asset_names, "Payload archive missing from release!"
            # Ensure old zip is gone
            assert "GRC-Risk-Register-Windows.zip" not in asset_names, "Old Windows zip still present in release!"

        run_step("TEST D — GitHub Release Assets Audit", test_d_release_audit)

        print("\n=======================================================")
        print("  ALL TRUE SINGLE-EXE BOOTSTRAP CHECKS PASSED (100%)")
        print("=======================================================\n")

    finally:
        kill_port_8000()
        shutil.rmtree(sandbox, ignore_errors=True)

if __name__ == "__main__":
    main()
