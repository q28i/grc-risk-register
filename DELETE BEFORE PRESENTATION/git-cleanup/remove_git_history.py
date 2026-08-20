"""
GRC Risk Register — Automatic Safe Git History Removal Tool
===========================================================
Automatically discovers the installed project root relative to its own location,
verifies safety markers, and removes all Git metadata without any user prompts.

Safety Invariants:
1. NEVER prompts the user for paths or inputs.
2. Automatically resolves PROJECT_ROOT by locating the parent containing "Grc Risk Management Code".
3. Validates required installation safety markers before taking any action.
4. Strictly scoped to the resolved PROJECT_ROOT (never touches external or parent directories).
5. Deletes ONLY .git directories, .gitignore, .gitattributes, .gitmodules.
6. Preserves all application source code, database, runtime, logs, and tools.
"""

import os
import sys
import shutil
import stat

def remove_readonly(func, path, excinfo):
    """Clear the read-only attribute and retry deletion."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def find_project_root():
    """Traverse upward from the current script location to locate the GRC project root."""
    current = os.path.dirname(os.path.abspath(__file__))
    
    # Check current directory and up to 5 parent levels
    for _ in range(6):
        has_app_code = os.path.isdir(os.path.join(current, "Grc Risk Management Code"))
        has_marker = (
            os.path.exists(os.path.join(current, "Start GRC Risk Register.exe")) or
            os.path.exists(os.path.join(current, "README.md")) or
            os.path.exists(os.path.join(current, "requirements.txt"))
        )
        if has_app_code and has_marker:
            return os.path.abspath(current)
        
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
        
    return None

def clean_git_metadata(project_root):
    """Recursively removes all Git metadata and repository history from project_root."""
    print("=======================================================")
    print("  GRC Risk Register — Git History Removal Tool")
    print("=======================================================")
    print(f"\n[INFO] Target Project Root: {project_root}")

    removed_items = []
    failed_items = []

    # 1. Search and delete all .git directories recursively inside project_root
    for root, dirs, files in os.walk(project_root, topdown=False):
        for d in list(dirs):
            if d.lower() == ".git":
                git_dir_path = os.path.join(root, d)
                print(f"[REMOVING] Deleting Git repository folder: {git_dir_path}")
                try:
                    # Clear read-only attributes recursively
                    for sub_root, sub_dirs, sub_files in os.walk(git_dir_path):
                        for sf in sub_files:
                            try: os.chmod(os.path.join(sub_root, sf), stat.S_IWRITE)
                            except Exception: pass
                        for sd in sub_dirs:
                            try: os.chmod(os.path.join(sub_root, sd), stat.S_IWRITE)
                            except Exception: pass
                    
                    shutil.rmtree(git_dir_path, onerror=remove_readonly)
                    if not os.path.exists(git_dir_path):
                        removed_items.append(git_dir_path)
                    else:
                        failed_items.append(git_dir_path)
                except Exception as e:
                    print(f"[ERROR] Could not delete {git_dir_path}: {e}")
                    failed_items.append(git_dir_path)

    # 2. Search and delete Git configuration/metadata files
    git_filenames = {".gitignore", ".gitattributes", ".gitmodules"}
    for root, dirs, files in os.walk(project_root):
        for f in files:
            if f.lower() in git_filenames:
                file_path = os.path.join(root, f)
                print(f"[REMOVING] Deleting Git configuration file: {file_path}")
                try:
                    os.chmod(file_path, stat.S_IWRITE)
                    os.remove(file_path)
                    removed_items.append(file_path)
                except Exception as e:
                    print(f"[ERROR] Could not delete {file_path}: {e}")
                    failed_items.append(file_path)

    # 3. Post-cleanup recursive audit
    remaining_git = []
    for root, dirs, files in os.walk(project_root):
        for d in dirs:
            if d.lower() == ".git":
                remaining_git.append(os.path.join(root, d))
        for f in files:
            if f.lower() in git_filenames:
                remaining_git.append(os.path.join(root, f))

    print("\n=======================================================")
    print("  CLEANUP SUMMARY")
    print("=======================================================")
    print(f"Items removed:   {len(removed_items)}")
    print(f"Items failed:    {len(failed_items)}")
    print(f"Remaining .git:  {len(remaining_git)}")

    if len(remaining_git) == 0 and len(failed_items) == 0:
        print("\n[SUCCESS] Project is 100% clean of all Git metadata and version control history.")
        print("Source code, presentation database, and application runtime are intact.")
        return True
    else:
        print(f"\n[WARNING] Some Git artifacts could not be removed: {remaining_git + failed_items}")
        return False

def main():
    root = find_project_root()
    if not root:
        print("=======================================================")
        print("  GRC Risk Register — Git History Removal Tool")
        print("=======================================================")
        print("\n[ABORTED] Could not automatically locate the GRC project root.")
        print("Safety check failed: 'Grc Risk Management Code' folder not found in parent hierarchy.")
        print("Refusing to operate on unknown directory.")
        sys.exit(1)

    success = clean_git_metadata(root)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
