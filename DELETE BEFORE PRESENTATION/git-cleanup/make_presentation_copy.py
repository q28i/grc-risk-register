"""
Presentation Copy Generator (Non-Destructive Cleanup)
Creates a pristine academic presentation copy in a separate directory.
Includes the deliberately configured SQLite presentation database.
NEVER modifies the original development repository.
"""

import os
import sys
import shutil
import argparse
import sqlite3

def make_presentation_copy(destination_dir=None, include_configured_db=True):
    curr_script_dir = os.path.dirname(os.path.abspath(__file__))
    dev_root = os.path.dirname(os.path.dirname(curr_script_dir))

    if not destination_dir:
        destination_dir = os.path.join(dev_root, "presentation_copy", "GRC_Risk_Register")

    print(f"=======================================================")
    print(f"  GRC Risk Register - Presentation Copy Generator")
    print(f"=======================================================")
    print(f"[Source Root]      : {dev_root}")
    print(f"[Destination Copy] : {destination_dir}")

    # Safety check: Destination must NOT be source directory
    if os.path.abspath(destination_dir) == os.path.abspath(dev_root):
        raise ValueError("FATAL: Destination cannot be the original development directory!")

    if os.path.exists(destination_dir):
        print(f"[Cleanup] Clearing existing destination directory: {destination_dir}")
        shutil.rmtree(destination_dir, ignore_errors=True)
    os.makedirs(destination_dir, exist_ok=True)

    # 1. Copy Core Root Distribution Files
    root_include = [
        "Start GRC Risk Register.exe",
        "Start GRC Risk Register.bat",
        "README.md",
        "LICENSE",
        "NOTICE",
        "VERSION",
        "requirements.txt",
        "GRC_Risk_Register_Project_Report.pdf",
        "GRC_Risk_Register_Presentation.pptx"
    ]

    for rf in root_include:
        src = os.path.join(dev_root, rf)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(destination_dir, rf))
            print(f"  [Copied Root] {rf}")

    # 2. Copy Sanitized Application Source (Grc Risk Management Code)
    src_app = os.path.join(dev_root, "Grc Risk Management Code")
    dst_app = os.path.join(destination_dir, "Grc Risk Management Code")
    os.makedirs(dst_app, exist_ok=True)

    exclude_dirs = {"__pycache__", "assets_media", "runtime", "logs", ".venv", "env", ".git", "updates"}
    exclude_files = {
        "README_ADMIN.md", "Launcher.cs",
        "verify_chg0009.py", "verify_chg0010.py", "build_ui_renders.py",
        "generate_pdf_report.py", "generate_pptx_presentation.py"
    }

    for r, dirs, files in os.walk(src_app):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        rel_dir = os.path.relpath(r, src_app)
        target_dir = dst_app if rel_dir == "." else os.path.join(dst_app, rel_dir)
        os.makedirs(target_dir, exist_ok=True)

        for f in files:
            if f.endswith(".pyc") or f in exclude_files:
                continue
            if f.endswith(".db"):
                # Copy configured presentation database specifically
                if include_configured_db and f == "grc_risk_register.db":
                    src_f = os.path.join(r, f)
                    dst_f = os.path.join(target_dir, f)
                    shutil.copy2(src_f, dst_f)
                    print(f"  [Copied Configured DB] {f}")
                continue
            src_f = os.path.join(r, f)
            dst_f = os.path.join(target_dir, f)
            shutil.copy2(src_f, dst_f)

    print("  [Copied App]  Grc Risk Management Code/ (sanitized)")

    # If DB wasn't present in Grc Risk Management Code, check backups or initialize
    db_dest = os.path.join(dst_app, "grc_risk_register.db")
    if not os.path.exists(db_dest):
        backup_db = os.path.join(dev_root, "backups", "presentation_demo.db")
        if os.path.exists(backup_db):
            shutil.copy2(backup_db, db_dest)
            print(f"  [Restored DB from Backup] presentation_demo.db -> {db_dest}")

    # 3. Comprehensive Verification & Security Audit
    print("\n[Audit] Auditing generated presentation copy...")
    all_files = []
    for r, dirs, files in os.walk(destination_dir):
        for f in files:
            all_files.append(os.path.relpath(os.path.join(r, f), destination_dir))

    print(f"[Audit] Total presentation files: {len(all_files)}")
    assert not os.path.exists(os.path.join(destination_dir, ".git")), "FAIL: .git found in presentation copy!"
    assert not os.path.exists(os.path.join(destination_dir, "DELETE BEFORE PRESENTATION")), "FAIL: Tooling folder in presentation copy!"
    assert not any("README_ADMIN" in f for f in all_files), "FAIL: Private README_ADMIN in presentation copy!"
    assert not any("Launcher.cs" in f for f in all_files), "FAIL: Launcher.cs in presentation copy!"
    assert "README.md" in all_files, "FAIL: README.md missing!"
    assert "LICENSE" in all_files, "FAIL: LICENSE missing!"
    assert "NOTICE" in all_files, "FAIL: NOTICE missing!"
    assert "Start GRC Risk Register.exe" in all_files, "FAIL: Launcher missing!"

    # Verify database contents if DB is included
    if os.path.exists(db_dest):
        conn = sqlite3.connect(db_dest)
        c = conn.cursor()
        users_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        fc_count = c.execute("SELECT COUNT(*) FROM feature_controls").fetchone()[0]
        assets_count = c.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        risks_count = c.execute("SELECT COUNT(*) FROM risks").fetchone()[0]
        conn.close()
        print(f"[Audit DB] Presentation DB Verified: {users_count} users, {fc_count} feature controls, {assets_count} assets, {risks_count} risks.")
        assert users_count >= 3, "Missing seed users!"
        assert fc_count >= 29, "Missing feature controls!"
        assert assets_count >= 1, "Missing assets!"
        assert risks_count >= 1, "Missing risks!"

    print("=======================================================")
    print("  PRESENTATION COPY READY AT:")
    print(f"  {destination_dir}")
    print("=======================================================\n")
    return destination_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a clean academic presentation copy of GRC Risk Register.")
    parser.add_argument("--dest", default=None, help="Target destination directory for presentation copy")
    parser.add_argument("--no-db", action="store_true", help="Do not copy existing database (test fresh install mode)")
    args = parser.parse_args()
    make_presentation_copy(args.dest, include_configured_db=not args.no_db)
