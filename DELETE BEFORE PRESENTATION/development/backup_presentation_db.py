"""
Development Backup Utility for Presentation Database
Snapshots and restores the configured presentation database.
DEVELOPMENT USE ONLY. Private backups are excluded from Git/release.
"""

import os
import sys
import shutil
import argparse

def get_paths():
    curr_script_dir = os.path.dirname(os.path.abspath(__file__))
    dev_root = os.path.dirname(os.path.dirname(curr_script_dir))
    app_db = os.path.join(dev_root, "Grc Risk Management Code", "grc_risk_register.db")
    backup_dir = os.path.join(dev_root, "backups")
    backup_db = os.path.join(backup_dir, "presentation_demo.db")
    return app_db, backup_dir, backup_db

def backup():
    app_db, backup_dir, backup_db = get_paths()
    if not os.path.exists(app_db):
        print(f"[Backup Error] No active database found at: {app_db}")
        return False
    os.makedirs(backup_dir, exist_ok=True)
    shutil.copy2(app_db, backup_db)
    print(f"[Backup Success] Saved presentation DB snapshot:")
    print(f"  Source : {app_db} ({os.path.getsize(app_db):,} bytes)")
    print(f"  Backup : {backup_db}")
    return True

def restore():
    app_db, backup_dir, backup_db = get_paths()
    if not os.path.exists(backup_db):
        print(f"[Restore Error] No backup snapshot found at: {backup_db}")
        return False
    os.makedirs(os.path.dirname(app_db), exist_ok=True)
    shutil.copy2(backup_db, app_db)
    print(f"[Restore Success] Restored presentation DB snapshot:")
    print(f"  Backup : {backup_db}")
    print(f"  Target : {app_db} ({os.path.getsize(app_db):,} bytes)")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup or restore the configured presentation SQLite database.")
    parser.add_argument("--restore", action="store_true", help="Restore database from snapshot")
    args = parser.parse_args()
    if args.restore:
        restore()
    else:
        backup()
