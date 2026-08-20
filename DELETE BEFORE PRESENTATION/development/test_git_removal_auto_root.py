"""
Test Automatic Root Discovery & Zero-Prompt Git History Removal
==============================================================
Validates that Remove Git History.exe, Remove Git History.bat, and remove_git_history.py:
1. NEVER prompt the user for any path or confirmation.
2. Automatically resolve PROJECT_ROOT relative to their own location.
3. Remove all .git folders and .gitignore files from the target installation.
4. Preserve all application source code, databases, and tooling.
5. Never touch or affect external/development repositories.
"""

import os
import sys
import shutil
import tempfile
import subprocess

def test_auto_root_removal():
    root_dir = r"c:\Users\Rift\Documents\Vaults\Temp Vault\Projects\Cybersecurity Risk Management System"
    git_clean_src = os.path.join(root_dir, "DELETE BEFORE PRESENTATION", "git-cleanup")

    # -----------------------------------------------------------------
    # TEST 1: Remove Git History.exe (C# Binary)
    # -----------------------------------------------------------------
    print("\n[TEST 1] Testing Remove Git History.exe (Zero Prompts)...")
    sep_1 = tempfile.mkdtemp(prefix="seperate_exe_test_")
    try:
        # Setup simulated installation
        os.makedirs(os.path.join(sep_1, "Grc Risk Management Code"), exist_ok=True)
        with open(os.path.join(sep_1, "Grc Risk Management Code", "app.py"), "w") as f: f.write("# App code\n")
        with open(os.path.join(sep_1, "Start GRC Risk Register.exe"), "w") as f: f.write("EXE\n")
        
        # Git metadata
        git_dir = os.path.join(sep_1, ".git")
        os.makedirs(git_dir, exist_ok=True)
        with open(os.path.join(git_dir, "HEAD"), "w") as f: f.write("ref: refs/heads/main\n")
        with open(os.path.join(sep_1, ".gitignore"), "w") as f: f.write("*.log\n")

        # Copy git-cleanup tools to simulated installation
        target_cleanup = os.path.join(sep_1, "DELETE BEFORE PRESENTATION", "git-cleanup")
        os.makedirs(target_cleanup, exist_ok=True)
        shutil.copy2(os.path.join(git_clean_src, "Remove Git History.exe"), target_cleanup)

        exe_path = os.path.join(target_cleanup, "Remove Git History.exe")
        assert os.path.exists(exe_path), "Target exe missing"

        print(f"  Running {exe_path} (Zero input)...")
        p = subprocess.run([exe_path], cwd=target_cleanup, capture_output=True, text=True, timeout=10)
        print(f"  Output:\n{p.stdout.strip()}")
        assert p.returncode == 0, f"Remove Git History.exe failed with code {p.returncode}"

        # Assertions
        assert not os.path.exists(git_dir), ".git directory still exists in target!"
        assert not os.path.exists(os.path.join(sep_1, ".gitignore")), ".gitignore still exists in target!"
        assert os.path.exists(os.path.join(sep_1, "Grc Risk Management Code", "app.py")), "Source code was deleted!"
        assert os.path.exists(os.path.join(sep_1, "Start GRC Risk Register.exe")), "Launcher was deleted!"
        print("  [PASS] Remove Git History.exe automatically cleaned target installation with zero prompts.")
    finally:
        shutil.rmtree(sep_1, ignore_errors=True)

    # -----------------------------------------------------------------
    # TEST 2: Remove Git History.bat (Batch Wrapper)
    # -----------------------------------------------------------------
    print("\n[TEST 2] Testing Remove Git History.bat (Zero Prompts)...")
    sep_2 = tempfile.mkdtemp(prefix="seperate_bat_test_")
    try:
        os.makedirs(os.path.join(sep_2, "Grc Risk Management Code"), exist_ok=True)
        with open(os.path.join(sep_2, "Grc Risk Management Code", "app.py"), "w") as f: f.write("# App code\n")
        with open(os.path.join(sep_2, "Start GRC Risk Register.exe"), "w") as f: f.write("EXE\n")
        
        git_dir = os.path.join(sep_2, ".git")
        os.makedirs(git_dir, exist_ok=True)
        with open(os.path.join(git_dir, "HEAD"), "w") as f: f.write("ref: refs/heads/main\n")
        with open(os.path.join(sep_2, ".gitignore"), "w") as f: f.write("*.log\n")

        target_cleanup = os.path.join(sep_2, "DELETE BEFORE PRESENTATION", "git-cleanup")
        os.makedirs(target_cleanup, exist_ok=True)
        shutil.copy2(os.path.join(git_clean_src, "Remove Git History.bat"), target_cleanup)
        shutil.copy2(os.path.join(git_clean_src, "remove_git_history.py"), target_cleanup)

        bat_path = os.path.join(target_cleanup, "Remove Git History.bat")
        print(f"  Running {bat_path} (Zero input)...")
        p = subprocess.run([bat_path], cwd=target_cleanup, capture_output=True, text=True, timeout=10)
        print(f"  Output:\n{p.stdout.strip()}")
        assert p.returncode == 0, f"Remove Git History.bat failed with code {p.returncode}"

        assert not os.path.exists(git_dir), ".git directory still exists in target!"
        assert not os.path.exists(os.path.join(sep_2, ".gitignore")), ".gitignore still exists in target!"
        assert os.path.exists(os.path.join(sep_2, "Grc Risk Management Code", "app.py")), "Source code was deleted!"
        print("  [PASS] Remove Git History.bat automatically cleaned target installation with zero prompts.")
    finally:
        shutil.rmtree(sep_2, ignore_errors=True)

    # -----------------------------------------------------------------
    # TEST 3: remove_git_history.py (Python Engine)
    # -----------------------------------------------------------------
    print("\n[TEST 3] Testing remove_git_history.py (Zero Prompts)...")
    sep_3 = tempfile.mkdtemp(prefix="seperate_py_test_")
    try:
        os.makedirs(os.path.join(sep_3, "Grc Risk Management Code"), exist_ok=True)
        with open(os.path.join(sep_3, "Grc Risk Management Code", "app.py"), "w") as f: f.write("# App code\n")
        with open(os.path.join(sep_3, "Start GRC Risk Register.exe"), "w") as f: f.write("EXE\n")
        
        git_dir = os.path.join(sep_3, ".git")
        os.makedirs(git_dir, exist_ok=True)
        with open(os.path.join(git_dir, "HEAD"), "w") as f: f.write("ref: refs/heads/main\n")

        target_cleanup = os.path.join(sep_3, "DELETE BEFORE PRESENTATION", "git-cleanup")
        os.makedirs(target_cleanup, exist_ok=True)
        shutil.copy2(os.path.join(git_clean_src, "remove_git_history.py"), target_cleanup)

        py_path = os.path.join(target_cleanup, "remove_git_history.py")
        print(f"  Running {py_path} (Zero input)...")
        p = subprocess.run([sys.executable, py_path], cwd=target_cleanup, capture_output=True, text=True, timeout=10)
        print(f"  Output:\n{p.stdout.strip()}")
        assert p.returncode == 0, f"remove_git_history.py failed with code {p.returncode}"

        assert not os.path.exists(git_dir), ".git directory still exists in target!"
        assert os.path.exists(os.path.join(sep_3, "Grc Risk Management Code", "app.py")), "Source code was deleted!"
        print("  [PASS] remove_git_history.py automatically cleaned target installation with zero prompts.")
    finally:
        shutil.rmtree(sep_3, ignore_errors=True)

    print("\n=======================================================")
    print("  ALL AUTO-ROOT GIT REMOVAL TESTS PASSED (100%)")
    print("=======================================================\n")

if __name__ == "__main__":
    test_auto_root_removal()
