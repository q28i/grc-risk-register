"""
Official Release Packaging Pipeline for Full Project Payload Distribution
==========================================================================
Builds:
- GRC-Risk-Register-Payload.zip (Application payload + DELETE BEFORE PRESENTATION tools)

Payload Structure:
├── Grc Risk Management Code/
│   ├── app.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── risk_calculator.py
│   ├── seed_data.py
│   ├── run_tests.py
│   ├── grc_risk_register.db
│   ├── static/
│   ├── templates/
│   └── tests/
├── DELETE BEFORE PRESENTATION/
│   ├── updater/
│   │   ├── updater.py
│   │   ├── updater_config.json
│   │   ├── test_updater.py
│   │   └── README.md
│   ├── git-cleanup/
│   │   ├── remove_git_history.bat
│   │   ├── remove_git_history.ps1
│   │   ├── make_presentation_copy.py
│   │   └── README.md
│   ├── release/
│   │   ├── build_release_zip.py
│   │   └── Launcher.cs
│   └── development/
│       ├── test_true_single_exe_bootstrap.py
│       ├── test_portable_self_contained_e2e.py
│       └── other test utilities
├── README.md
├── LICENSE
├── NOTICE
├── VERSION
└── requirements.txt

Payload Invariants:
- Configured presentation SQLite database (grc_risk_register.db) included
- Static assets (static/) and HTML templates (templates/) included
- Standard metadata files (README.md, LICENSE, NOTICE, VERSION, requirements.txt) included
- DELETE BEFORE PRESENTATION/ directory with updater, git-cleanup, release, development included
- ZERO root/payload executables or batch scripts
- ZERO .git metadata
"""

import os
import shutil
import tempfile
import zipfile
import sqlite3

def build_payload_package():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(curr_dir))
    payload_zip_path = os.path.join(root_dir, "GRC-Risk-Register-Payload.zip")

    print("=======================================================")
    print("  BUILDING COMPLETE PORTABLE PROJECT PAYLOAD")
    print(f"  Target: {payload_zip_path}")
    print("=======================================================")

    if os.path.exists(payload_zip_path):
        try:
            os.remove(payload_zip_path)
            print(f"[Clean] Removed old payload archive.")
        except Exception as e:
            print(f"[Warning] Could not remove {payload_zip_path}: {e}")

    # Verify source database
    source_db = os.path.join(root_dir, "Grc Risk Management Code", "grc_risk_register.db")
    assert os.path.exists(source_db), f"Configured database missing at: {source_db}"

    # Audit source database records
    conn = sqlite3.connect(source_db)
    c = conn.cursor()
    user_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    fc_count = c.execute("SELECT COUNT(*) FROM feature_controls").fetchone()[0]
    asset_count = c.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    risk_count = c.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
    conn.close()
    print(f"[Database Audit] Verified presentation DB: {user_count} users, {fc_count} controls, {asset_count} assets, {risk_count} risks.")
    assert user_count >= 3, "Presentation database missing required users!"
    assert fc_count >= 29, "Presentation database missing feature controls!"

    staging_dir = tempfile.mkdtemp(prefix="grc_full_payload_")

    try:
        exclude_dirs = {"__pycache__", "assets_media", "runtime", "logs", ".venv", "env", ".git", ".idea", ".vscode"}
        exclude_files = {
            "Start GRC Risk Register.exe", "Start GRC Risk Register.bat",
            "Start.GRC.Risk.Register.exe", "GRC-Risk-Register-Payload.zip",
            "GRC-Risk-Register-Windows.zip", "GRC_Risk_Register_Project_Report.pdf",
            "GRC_Risk_Register_Presentation.pptx"
        }

        # 1. Copy Grc Risk Management Code
        app_source = os.path.join(root_dir, "Grc Risk Management Code")
        app_target = os.path.join(staging_dir, "Grc Risk Management Code")
        for root, dirs, files in os.walk(app_source):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            rel_dir = os.path.relpath(root, app_source)
            target_dir = os.path.join(app_target, rel_dir) if rel_dir != "." else app_target
            os.makedirs(target_dir, exist_ok=True)

            for f in files:
                if f.endswith(".pyc") or f in exclude_files or f.endswith(".zip") or f.endswith(".exe"):
                    continue
                shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))

        # 2. Copy DELETE BEFORE PRESENTATION
        del_source = os.path.join(root_dir, "DELETE BEFORE PRESENTATION")
        del_target = os.path.join(staging_dir, "DELETE BEFORE PRESENTATION")
        for root, dirs, files in os.walk(del_source):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            rel_dir = os.path.relpath(root, del_source)
            target_dir = os.path.join(del_target, rel_dir) if rel_dir != "." else del_target
            os.makedirs(target_dir, exist_ok=True)

            for f in files:
                if f.endswith(".pyc") or f in exclude_files or f.endswith(".zip") or f.endswith(".exe"):
                    continue
                shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))

        # 3. Copy root metadata files
        for mf in ["README.md", "LICENSE", "NOTICE", "VERSION", "requirements.txt"]:
            src = os.path.join(root_dir, mf)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(staging_dir, mf))

        # Write Payload ZIP
        with zipfile.ZipFile(payload_zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(staging_dir):
                for f in files:
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, staging_dir)
                    zip_entry_name = rel_path.replace("\\", "/")
                    z.write(full_path, zip_entry_name)

        print(f"[Success] Built {payload_zip_path} ({os.path.getsize(payload_zip_path):,} bytes).")

    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)

    # Validate Payload Invariants
    print("\n[Validation] Validating payload package...")
    with zipfile.ZipFile(payload_zip_path, "r") as z:
        entries = z.namelist()
        print(f"  Payload entries: {len(entries)}")

        # Required application files
        assert "Grc Risk Management Code/app.py" in entries, "app.py missing in payload!"
        assert "Grc Risk Management Code/grc_risk_register.db" in entries, "grc_risk_register.db missing in payload!"
        assert "Grc Risk Management Code/static/js/app.js" in entries, "static/js/app.js missing in payload!"
        assert "Grc Risk Management Code/templates/index.html" in entries, "templates/index.html missing in payload!"
        assert "README.md" in entries, "README.md missing in payload!"
        assert "VERSION" in entries, "VERSION missing in payload!"

        # Required development/presentation tools in DELETE BEFORE PRESENTATION
        assert "DELETE BEFORE PRESENTATION/updater/updater.py" in entries, "updater.py missing in payload!"
        assert "DELETE BEFORE PRESENTATION/git-cleanup/remove_git_history.bat" in entries, "remove_git_history.bat missing in payload!"
        assert "DELETE BEFORE PRESENTATION/git-cleanup/remove_git_history.ps1" in entries, "remove_git_history.ps1 missing in payload!"
        assert "DELETE BEFORE PRESENTATION/release/Launcher.cs" in entries, "Launcher.cs missing in payload!"

        # Strict exclusions
        assert not any(e.endswith(".exe") for e in entries), "Executable found in payload!"
        assert not any(e.startswith(".git") or "/.git" in e for e in entries), ".git found in payload!"

    print("\n=======================================================")
    print("  COMPLETE PROJECT PAYLOAD BUILT & VALIDATED (100%)")
    print("=======================================================\n")

if __name__ == "__main__":
    build_payload_package()
