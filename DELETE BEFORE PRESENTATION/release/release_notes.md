# Release Packaging Notes

This directory contains release build scripts for packaging public Windows distribution archives.

---

## Release Architecture

The release package (`GRC-Risk-Register-Windows.zip`) contains:

1. **Executable & Batch Launchers**:
   - `Start GRC Risk Register.exe` (native Windows GUI launcher with runtime auto-bootstrap)
   - `Start GRC Risk Register.bat` (batch script fallback launcher)
2. **Application Core**:
   - `Grc Risk Management Code/` (pure Python 3 standard library application)
3. **Academic Documentation**:
   - `GRC_Risk_Register_Project_Report.pdf` (10-page academic report)
   - `GRC_Risk_Register_Presentation.pptx` (10-slide academic presentation)
4. **Legal & Attribution**:
   - `LICENSE` (Apache 2.0)
   - `NOTICE` (OWASP IT GRC project attribution)
   - `VERSION` (single version source of truth)
   - `requirements.txt` (standard library declaration)
   - `README.md` (clean public quick start guide)

---

## Building the Release Archive

```bash
python "DELETE BEFORE PRESENTATION/release/build_release_zip.py"
```
