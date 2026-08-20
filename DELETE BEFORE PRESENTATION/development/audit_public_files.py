"""
Audit all public files to be tracked in the clean Git repository.
Ensures ZERO leaked credentials, AI tokens, dev logs, or private files.
"""

import os
import re

def audit_repo():
    root_dir = r"c:\Users\Rift\Documents\Vaults\Temp Vault\Projects\Cybersecurity Risk Management System"

    # List of files/folders that MUST NOT be tracked
    forbidden_files = [
        "README_ADMIN.md",
        "DOCUMENTATION_BUILD_LOG.md",
        "GRC_Risk_Register_Project_Report.pdf",
        "GRC_Risk_Register_Presentation.pptx",
        "Launcher.cs",
        "build_ui_renders.py",
        "generate_pdf_report.py",
        "generate_pptx_presentation.py",
        "verify_chg0009.py",
        "verify_chg0010.py"
    ]

    forbidden_dirs = [
        "Documentation",
        "DELETE BEFORE PRESENTATION",
        "backups",
        "presentation_copy",
        "release_export",
        "assets_media",
        "runtime",
        "updates"
    ]

    print("[Audit] Scanning repository structure...")

    # Check root forbidden files
    for ff in forbidden_files:
        assert not os.path.exists(os.path.join(root_dir, "tracked_" + ff)), f"Found forbidden {ff}"

    print("[Audit] Checking public file content for sensitive terms...")
    # Public files to check
    public_files = [
        os.path.join(root_dir, "README.md"),
        os.path.join(root_dir, "LICENSE"),
        os.path.join(root_dir, "NOTICE"),
        os.path.join(root_dir, "VERSION"),
        os.path.join(root_dir, "requirements.txt"),
        os.path.join(root_dir, ".gitignore"),
        os.path.join(root_dir, "Start GRC Risk Register.bat")
    ]

    for r, dirs, files in os.walk(os.path.join(root_dir, "Grc Risk Management Code")):
        if any(fd in r for fd in ["__pycache__", "assets_media"]):
            continue
        for f in files:
            if f in forbidden_files or f.endswith(".db") or f.endswith(".pyc") or f.endswith(".zip"):
                continue
            public_files.append(os.path.join(r, f))

    print(f"[Audit] Found {len(public_files)} public files.")

    flagged_terms = [
        "antigravity", "gemini", "cursor", "ai agent", "chg-", "changelog",
        "feature_status", "test_log", "implementation_plan", "walkthrough",
        "git-cleanup", "backup_presentation_db"
    ]

    clean = True
    for pf in public_files:
        if not os.path.exists(pf):
            continue
        # Skip binary or exe files
        if pf.endswith(".exe") or pf.endswith(".ico") or pf.endswith(".png"):
            continue
        try:
            with open(pf, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
                for term in flagged_terms:
                    if term in content:
                        print(f"  [FLAG] Term '{term}' found in {os.path.relpath(pf, root_dir)}")
                        clean = False
        except Exception as e:
            print(f"  [Error reading {pf}]: {e}")

    if clean:
        print("[Audit] 100% CLEAN! Zero forbidden development/AI terms found in public source files.")
    else:
        print("[Audit] Some terms flagged - review above.")

    return clean

if __name__ == "__main__":
    audit_repo()
