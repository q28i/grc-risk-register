#!/usr/bin/env python3
"""
Clean Distribution Packager for College Showcase & Presentation.

Generates two strictly separated ZIP archives:
1. GRC-Risk-Register-Source.zip (Source Code Only)
   - Contains clean, runnable application code, runtime launcher, requirements, assets, and tests.
   - Strictly excludes reports, documentation markdown, PDFs, presentations, git folders, and developer tools.

2. GRC-Risk-Register-Documentation.zip (Documentation & Presentation Only)
   - Contains Project Report PDF, Presentation PPTX, README, LICENSE, NOTICE, and academic documentation.
   - Strictly excludes source code and internal databases.
"""

import os
import zipfile
import shutil

# Script is located in DELETE BEFORE PRESENTATION/release/
RELEASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(RELEASE_DIR))
OUTPUT_SOURCE_ZIP = os.path.join(ROOT_DIR, "GRC-Risk-Register-Source.zip")
OUTPUT_DOCS_ZIP = os.path.join(ROOT_DIR, "GRC-Risk-Register-Documentation.zip")

# Source distribution files
SOURCE_INCLUDES = [
    # Core app folder
    ("Grc Risk Management Code", "Grc Risk Management Code"),
    # Requirements
    ("requirements.txt", "requirements.txt"),
    # Windows Standalone Launcher
    ("Start GRC Risk Register.exe", "Start GRC Risk Register.exe"),
]

# Files/patterns to exclude from Source ZIP
SOURCE_EXCLUDES = [
    "__pycache__",
    ".pyc",
    ".git",
    ".gitignore",
    "generate_pdf_report.py",
    "generate_pptx_presentation.py",
    "build_ui_renders.py",
    "verify_chg0009.py",
    "verify_chg0010.py",
    "README.md",
    "LICENSE",
    "NOTICE",
    "VERSION"
]

# Documentation distribution files
DOCS_INCLUDES = [
    ("GRC_Risk_Register_Project_Report.pdf", "GRC_Risk_Register_Project_Report.pdf"),
    ("GRC_Risk_Register_Presentation.pptx", "GRC_Risk_Register_Presentation.pptx"),
    ("README.md", "README.md"),
    ("README_ADMIN.md", "README_ADMIN.md"),
    ("DOCUMENTATION_BUILD_LOG.md", "DOCUMENTATION_BUILD_LOG.md"),
    ("LICENSE", "LICENSE"),
    ("VERSION", "VERSION"),
    ("Documentation", "Documentation"),
]

def build_source_zip():
    print(f"[1/2] Building Source Code ZIP: {OUTPUT_SOURCE_ZIP}...")
    if os.path.exists(OUTPUT_SOURCE_ZIP):
        os.remove(OUTPUT_SOURCE_ZIP)

    with zipfile.ZipFile(OUTPUT_SOURCE_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in SOURCE_INCLUDES:
            full_src = os.path.join(ROOT_DIR, src)
            if not os.path.exists(full_src):
                print(f"  WARNING: Source file {src} not found!")
                continue

            if os.path.isfile(full_src):
                zf.write(full_src, arcname)
                print(f"  + Added file: {arcname}")
            elif os.path.isdir(full_src):
                for dirpath, dirnames, filenames in os.walk(full_src):
                    dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
                    for filename in filenames:
                        if any(filename.endswith(ext) for ext in (".pyc", ".pyo")):
                            continue
                        if filename in SOURCE_EXCLUDES:
                            continue
                        
                        abs_file = os.path.join(dirpath, filename)
                        rel_path = os.path.relpath(abs_file, full_src)
                        target_arc = os.path.join(arcname, rel_path).replace("\\", "/")
                        zf.write(abs_file, target_arc)
    
    size_mb = os.path.getsize(OUTPUT_SOURCE_ZIP) / (1024 * 1024)
    print(f"  -> Successfully created Source ZIP ({size_mb:.2f} MB)")


def build_docs_zip():
    print(f"[2/2] Building Documentation ZIP: {OUTPUT_DOCS_ZIP}...")
    if os.path.exists(OUTPUT_DOCS_ZIP):
        os.remove(OUTPUT_DOCS_ZIP)

    with zipfile.ZipFile(OUTPUT_DOCS_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in DOCS_INCLUDES:
            full_src = os.path.join(ROOT_DIR, src)
            if not os.path.exists(full_src):
                print(f"  WARNING: Doc file {src} not found!")
                continue

            if os.path.isfile(full_src):
                zf.write(full_src, arcname)
                print(f"  + Added file: {arcname}")
            elif os.path.isdir(full_src):
                for dirpath, dirnames, filenames in os.walk(full_src):
                    dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
                    for filename in filenames:
                        if any(filename.endswith(ext) for ext in (".pyc", ".pyo")):
                            continue
                        abs_file = os.path.join(dirpath, filename)
                        rel_path = os.path.relpath(abs_file, full_src)
                        target_arc = os.path.join(arcname, rel_path).replace("\\", "/")
                        zf.write(abs_file, target_arc)

    size_mb = os.path.getsize(OUTPUT_DOCS_ZIP) / (1024 * 1024)
    print(f"  -> Successfully created Documentation ZIP ({size_mb:.2f} MB)")


if __name__ == "__main__":
    build_source_zip()
    build_docs_zip()
    print("\nPackaging completed successfully!")
