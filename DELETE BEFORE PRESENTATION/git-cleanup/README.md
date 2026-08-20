# Git & Presentation Cleanup Tooling

This directory contains automated tooling to generate a pristine, presentation-ready academic copy of the GRC Risk Register project without development metadata.

---

## Tooling Overview

- **`make_presentation_copy.py`**:
  - Automatically exports only production-ready application source files, launchers, PDF reports, presentations, and legal notices into a separate directory.
  - **Strictly Non-Destructive**: Operates exclusively on a new copy and never modifies or deletes files in the working development repository.

---

## What is Excluded from the Presentation Copy

1. **Development Tooling**: `DELETE BEFORE PRESENTATION/`, `updater/`, packaging scripts.
2. **Git Metadata**: `.git/` directory and commit history.
3. **Private Documentation**: `README_ADMIN.md`, internal roadmaps, build logs.
4. **Development Databases & Logs**: `*.db`, `*.sqlite`, `logs/`, `updates/`.
5. **Compilation & Scratch Files**: `Launcher.cs`, `__pycache__/`, temporary test scripts.

---

## What is Preserved in the Presentation Copy

1. **Core Application**: `app.py`, `database.py`, `models.py`, `auth.py`, `risk_calculator.py`, `seed_data.py`.
2. **User Interface**: `templates/index.html`, `static/css/style.css`, `static/js/app.js`, `static/js/dashboard.js`, `static/js/reports.js`.
3. **Launchers**: `Start GRC Risk Register.exe` and `Start GRC Risk Register.bat`.
4. **Automated Test Suite**: `run_tests.py` and `tests/`.
5. **Legal Attribution**: `LICENSE` (Apache 2.0) and `NOTICE` (OWASP IT GRC project attribution).
6. **Academic Package**: `GRC_Risk_Register_Project_Report.pdf` and `GRC_Risk_Register_Presentation.pptx`.

---

## Usage

```bash
python "DELETE BEFORE PRESENTATION/git-cleanup/make_presentation_copy.py" --dest "C:/path/to/destination"
```
