# Development & Release Tooling (DELETE BEFORE PRESENTATION)

> **Important**: This entire directory contains development, release packaging, Git cleanup, and updater tooling used during software engineering. It is **not** required for the academic presentation copy and can be safely deleted or removed prior to evaluator demonstration.

---

## Directory Overview

```text
DELETE BEFORE PRESENTATION/
├── updater/
│   ├── updater.py               # GitHub Releases automated update engine
│   ├── updater_config.json      # Repository & asset target configuration
│   ├── test_updater.py          # Updater unit test suite
│   └── README.md                # Updater documentation
├── git-cleanup/
│   ├── make_presentation_copy.py # Safe generator for clean presentation copies
│   ├── remove_git.bat           # Interactive Windows script to remove .git from copy
│   ├── remove_git.ps1           # Interactive PowerShell script to remove .git from copy
│   └── README.md                # Git cleanup documentation
├── release/
│   ├── build_release_zip.py     # Standalone distribution ZIP packaging script
│   └── release_notes.md         # Windows release packaging documentation
├── development/
│   ├── backup_presentation_db.py # Development snapshot utility for SQLite database
│   ├── audit_public_files.py    # Public repository security scan script
│   ├── test_chg0014_presentation_copy.py
│   ├── test_chg0015_presentation_persistence.py
│   ├── test_semester2_final_verification.py
│   └── README.md                # Development utilities index
└── README.md                    # This tooling index
```

---

## Workflow: Generating a Clean Presentation Copy

To prepare a clean demonstration folder for presentation:

```bash
python "DELETE BEFORE PRESENTATION/git-cleanup/make_presentation_copy.py" --dest "C:/path/to/GRC_Risk_Register_Presentation_Copy"
```

The output folder will be ready to double-click and run with zero development artifacts.
