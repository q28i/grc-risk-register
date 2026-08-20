# Application Updater Tooling

This directory contains the GitHub Releases updater engine and tests.

---

## Files

- **`updater.py`**: Safe updater module that queries GitHub Releases over HTTPS, downloads updates, stages, backs up existing files, applies updates while preserving SQLite databases, and rolls back on failure.
- **`updater_config.json`**: Updater configuration targeting `q28i/grc-risk-register`.
- **`test_updater.py`**: Automated unit test suite verifying updater version parsing, database preservation, and rollback mechanisms.
