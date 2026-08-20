"""
GRC Risk Register — Safe Presentation Git Removal Tool
=====================================================
Safely removes the .git/ directory from a specified target copy of the project.

Safety Invariants:
1. NEVER operates on the active working tree silently.
2. Requires explicit target directory specification and user confirmation.
3. Deletes ONLY the .git/ folder.
4. Preserves all application source code, databases, templates, and documentation.
"""

import os
import sys
import shutil
import stat
import argparse

def remove_readonly(func, path, excinfo):
    """Clear the read-only bit and retry removal."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def remove_git_history(target_dir, force=False):
    target_path = os.path.abspath(target_dir)

    print("=======================================================")
    print("  GRC Risk Register — Presentation Git Removal Tool")
    print("=======================================================")
    print(f"\nTarget directory: {target_path}")

    if not os.path.isdir(target_path):
        print(f"[ERROR] Target directory does not exist: {target_path}")
        return False

    git_dir = os.path.join(target_path, ".git")

    if not os.path.exists(git_dir):
        print(f"[INFO] No .git directory found at: {git_dir}")
        print("[INFO] Nothing to remove.")
        return True

    print(f"[FOUND] Git version history found at: {git_dir}")
    print("\nWARNING: This will permanently delete the Git history from THIS target copy.")
    print("Source files, templates, and database will remain completely untouched.")
    print("=======================================================")

    if not force:
        try:
            confirm = input(f"\nAre you sure you want to permanently remove Git history from THIS COPY? (Y/N): ").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return False

        if confirm not in ("Y", "YES"):
            print("[CANCELLED] Operation cancelled by user. No changes made.")
            return False

    print("\n[REMOVING] Deleting .git directory...")
    try:
        # Clear attributes and remove tree
        for root, dirs, files in os.walk(git_dir):
            for f in files:
                p = os.path.join(root, f)
                try: os.chmod(p, stat.S_IWRITE)
                except Exception: pass
            for d in dirs:
                p = os.path.join(root, d)
                try: os.chmod(p, stat.S_IWRITE)
                except Exception: pass

        shutil.rmtree(git_dir, onerror=remove_readonly)

        if not os.path.exists(git_dir):
            print(f"[SUCCESS] Git history (.git/) removed successfully from:\n  {target_path}")
            return True
        else:
            print(f"[ERROR] Failed to completely remove .git directory.")
            return False
    except Exception as e:
        print(f"[ERROR] Exception during removal: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Safely remove .git history from a target presentation copy.")
    parser.add_argument("target", nargs="?", default="", help="Path to target directory to clean")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    target = args.target.strip()
    if not target:
        print("=======================================================")
        print("  GRC Risk Register — Presentation Git Removal Tool")
        print("=======================================================")
        print("\nPlease enter the path to the presentation copy folder you wish to clean.")
        print("Example: C:\\Users\\Name\\Desktop\\Presentation Copy\n")
        try:
            target = input("Enter target folder path: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(1)

        if not target:
            print("[ERROR] No target folder specified. Refusing to operate on unknown directory.")
            sys.exit(1)

    success = remove_git_history(target, force=args.yes)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
