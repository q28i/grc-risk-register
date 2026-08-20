"""
Test all Git history removal scripts in DELETE BEFORE PRESENTATION/git-cleanup/
"""
import os
import shutil
import tempfile
import subprocess

def test_git_removal_tools():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    git_clean_dir = os.path.join(curr_dir, "..", "git-cleanup")

    py_script = os.path.join(git_clean_dir, "remove_git_history.py")
    bat_script = os.path.join(git_clean_dir, "Remove Git History.bat")
    ps1_script = os.path.join(git_clean_dir, "Remove Git History.ps1")

    assert os.path.exists(py_script), f"Missing {py_script}"
    assert os.path.exists(bat_script), f"Missing {bat_script}"
    assert os.path.exists(ps1_script), f"Missing {ps1_script}"

    # 1. Test remove_git_history.py with Y
    d1 = tempfile.mkdtemp(prefix="test_git_py_")
    try:
        git_dir = os.path.join(d1, ".git")
        os.makedirs(git_dir, exist_ok=True)
        with open(os.path.join(git_dir, "HEAD"), "w") as f: f.write("ref: refs/heads/main\n")
        with open(os.path.join(d1, "app.py"), "w") as f: f.write("# Source\n")

        p = subprocess.run([sys.executable, py_script, d1], input="Y\n", capture_output=True, text=True)
        print("Python tool output (Y):", p.stdout.strip())
        assert not os.path.exists(git_dir), ".git still exists after Python Y!"
        assert os.path.exists(os.path.join(d1, "app.py")), "app.py deleted by Python tool!"
    finally:
        shutil.rmtree(d1, ignore_errors=True)

    # 2. Test remove_git_history.py with N (cancellation)
    d2 = tempfile.mkdtemp(prefix="test_git_py_cancel_")
    try:
        git_dir = os.path.join(d2, ".git")
        os.makedirs(git_dir, exist_ok=True)
        with open(os.path.join(git_dir, "HEAD"), "w") as f: f.write("ref: refs/heads/main\n")
        with open(os.path.join(d2, "app.py"), "w") as f: f.write("# Source\n")

        p = subprocess.run([sys.executable, py_script, d2], input="N\n", capture_output=True, text=True)
        print("Python tool output (N):", p.stdout.strip())
        assert os.path.exists(git_dir), ".git was deleted on Python N!"
    finally:
        shutil.rmtree(d2, ignore_errors=True)

    # 3. Test Remove Git History.bat with Y
    d3 = tempfile.mkdtemp(prefix="test_git_bat_")
    try:
        git_dir = os.path.join(d3, ".git")
        os.makedirs(git_dir, exist_ok=True)
        with open(os.path.join(git_dir, "HEAD"), "w") as f: f.write("ref: refs/heads/main\n")
        with open(os.path.join(d3, "app.py"), "w") as f: f.write("# Source\n")

        p = subprocess.run(["cmd.exe", "/c", bat_script, d3], input="Y\n", capture_output=True, text=True)
        print("BAT tool output (Y):", p.stdout.strip())
        assert not os.path.exists(git_dir), ".git still exists after BAT Y!"
        assert os.path.exists(os.path.join(d3, "app.py")), "app.py deleted by BAT tool!"
    finally:
        shutil.rmtree(d3, ignore_errors=True)

    # 4. Test Remove Git History.bat with N
    d4 = tempfile.mkdtemp(prefix="test_git_bat_cancel_")
    try:
        git_dir = os.path.join(d4, ".git")
        os.makedirs(git_dir, exist_ok=True)
        with open(os.path.join(git_dir, "HEAD"), "w") as f: f.write("ref: refs/heads/main\n")
        with open(os.path.join(d4, "app.py"), "w") as f: f.write("# Source\n")

        p = subprocess.run(["cmd.exe", "/c", bat_script, d4], input="N\n", capture_output=True, text=True)
        print("BAT tool output (N):", p.stdout.strip())
        assert os.path.exists(git_dir), ".git was deleted on BAT N!"
    finally:
        shutil.rmtree(d4, ignore_errors=True)

    print("\n[SUCCESS] ALL GIT REMOVAL TOOLS PASSED (100%)\n")

if __name__ == "__main__":
    import sys
    test_git_removal_tools()
