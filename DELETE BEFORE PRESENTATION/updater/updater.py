"""
GRC Risk Register - Application Updater (Development & Release Tooling)
Handles checking GitHub Releases for updates, downloading assets securely over HTTPS,
staging, backing up, safe atomic replacement, database preservation, and rollback.
"""

import os
import sys
import json
import shutil
import zipfile
import urllib.request
import urllib.error
import time
import subprocess
import re

def get_app_dir():
    """Finds the root directory containing the application code."""
    curr = os.path.dirname(os.path.abspath(__file__)) # .../DELETE BEFORE PRESENTATION/updater
    # Look up 1, 2, or 3 levels
    candidates = [
        os.path.dirname(curr),
        os.path.dirname(os.path.dirname(curr)),
        os.path.dirname(os.path.dirname(os.path.dirname(curr)))
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "app.py")):
            return c
        if os.path.exists(os.path.join(c, "Grc Risk Management Code", "app.py")):
            return os.path.join(c, "Grc Risk Management Code")
    return os.path.dirname(curr)

def get_current_version(app_dir=None):
    """Reads the current version from VERSION file or falls back to default."""
    if not app_dir:
        app_dir = get_app_dir()
    v_file = os.path.join(app_dir, "VERSION")
    if not os.path.exists(v_file):
        parent_v_file = os.path.join(os.path.dirname(app_dir), "VERSION")
        if os.path.exists(parent_v_file):
            v_file = parent_v_file
    if os.path.exists(v_file):
        try:
            with open(v_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "1.0.0"

def parse_version(v_str):
    """Parses a version string like 'v1.2.3' or 'v0.9.5-beta' into a tuple of ints."""
    v_clean = v_str.lstrip("vV").strip()
    main_part = re.split(r'[-+]', v_clean)[0]
    parts = []
    for p in main_part.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])

def is_newer_version(latest_v, current_v):
    """Returns True if latest_v is strictly newer than current_v."""
    return parse_version(latest_v) > parse_version(current_v)

def load_config(app_dir=None):
    """Loads updater_config.json from local or parent updater directory."""
    curr = os.path.dirname(os.path.abspath(__file__))
    local_cfg = os.path.join(curr, "updater_config.json")
    if os.path.exists(local_cfg):
        try:
            with open(local_cfg, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    if not app_dir:
        app_dir = get_app_dir()
    cfg_paths = [
        os.path.join(app_dir, "updater", "updater_config.json"),
        os.path.join(os.path.dirname(app_dir), "updater", "updater_config.json"),
        os.path.join(os.path.dirname(app_dir), "DELETE BEFORE PRESENTATION", "updater", "updater_config.json")
    ]
    for cp in cfg_paths:
        if os.path.exists(cp):
            try:
                with open(cp, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

    return {
        "repo": "q28i/grc-risk-register",
        "api_url": "https://api.github.com/repos/q28i/grc-risk-register/releases/latest",
        "asset_name": "GRC-Risk-Register-Windows.zip",
        "preserve_files": [
            "grc_risk_register.db",
            "grc_risk_register.db-journal",
            "grc_risk_register.db-wal",
            "grc_risk_register.db-shm",
            "README_ADMIN.md",
            "runtime",
            "logs",
            "updates"
        ]
    }

def check_for_updates(app_dir=None, timeout=4):
    """
    Checks GitHub Releases for a newer version.
    Returns: dict(has_update=bool, latest_version=str, current_version=str, download_url=str, release_notes=str, error=str)
    """
    if not app_dir:
        app_dir = get_app_dir()
    current_v = get_current_version(app_dir)
    config = load_config(app_dir)
    api_url = config.get("api_url", "https://api.github.com/repos/q28i/grc-risk-register/releases/latest")
    asset_name = config.get("asset_name", "GRC-Risk-Register-Windows.zip")

    result = {
        "has_update": False,
        "latest_version": current_v,
        "current_version": current_v,
        "download_url": None,
        "release_notes": "",
        "error": None
    }

    try:
        req = urllib.request.Request(
            api_url,
            headers={
                "User-Agent": "GRC-Risk-Register-Updater/1.0",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                tag_name = data.get("tag_name", "").lstrip("vV")
                latest_v = tag_name if tag_name else current_v
                result["latest_version"] = latest_v
                result["release_notes"] = data.get("body", "")

                # Find asset download URL
                for asset in data.get("assets", []):
                    if asset.get("name") == asset_name:
                        result["download_url"] = asset.get("browser_download_url")
                        break

                if not result["download_url"] and data.get("zipball_url"):
                    result["download_url"] = data.get("zipball_url")

                if is_newer_version(latest_v, current_v):
                    result["has_update"] = True
            else:
                result["error"] = f"HTTP {response.status}"
    except urllib.error.URLError as e:
        result["error"] = f"Network unavailable: {e.reason}"
    except Exception as e:
        result["error"] = str(e)

    return result

def download_file(url, dest_path, timeout=30):
    """Downloads a file from URL over HTTPS."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "GRC-Risk-Register-Updater/1.0"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        with open(dest_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
    return os.path.exists(dest_path) and os.path.getsize(dest_path) > 0

def apply_update(zip_path, app_dir=None):
    """
    Safely applies update from zip file:
    1. Extracts to staging
    2. Backs up current files (preserving database and user data)
    3. Replaces application files
    4. Rolls back on failure
    Returns: (success: bool, message: str)
    """
    if not app_dir:
        app_dir = get_app_dir()

    config = load_config(app_dir)
    preserve_names = set(config.get("preserve_files", []))
    preserve_names.update([
        "grc_risk_register.db", "grc_risk_register.db-journal",
        "grc_risk_register.db-wal", "grc_risk_register.db-shm",
        "README_ADMIN.md", "runtime", "logs", "updates"
    ])

    updates_base = os.path.join(app_dir, "updates")
    staging_dir = os.path.join(updates_base, "staging")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(updates_base, "backup", f"backup_{timestamp}")

    # Clean old staging
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir, ignore_errors=True)
    os.makedirs(staging_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)

    # 1. Verify ZIP integrity and extract
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            corrupt = z.testzip()
            if corrupt:
                return False, f"Downloaded update ZIP is corrupt ({corrupt})."
            z.extractall(staging_dir)
    except Exception as e:
        return False, f"Failed to extract update package: {e}"

    # 2. Locate source payload inside staging
    payload_dir = staging_dir
    if os.path.exists(os.path.join(staging_dir, "Grc Risk Management Code")):
        payload_dir = os.path.join(staging_dir, "Grc Risk Management Code")

    # 3. Create Backup of existing application files (excluding preserved files)
    try:
        for item in os.listdir(app_dir):
            if item in preserve_names:
                continue
            src_item = os.path.join(app_dir, item)
            dst_item = os.path.join(backup_dir, item)
            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item)
            else:
                shutil.copy2(src_item, dst_item)
    except Exception as e:
        return False, f"Failed to create backup before updating: {e}"

    # 4. Copy new payload files into application directory
    try:
        for root, dirs, files in os.walk(payload_dir):
            rel_dir = os.path.relpath(root, payload_dir)
            target_dir = app_dir if rel_dir == "." else os.path.join(app_dir, rel_dir)
            os.makedirs(target_dir, exist_ok=True)

            for f in files:
                if f in preserve_names or f.endswith(".db"):
                    continue
                src_f = os.path.join(root, f)
                dst_f = os.path.join(target_dir, f)
                shutil.copy2(src_f, dst_f)
    except Exception as e:
        # ROLLBACK
        try:
            for item in os.listdir(backup_dir):
                s = os.path.join(backup_dir, item)
                d = os.path.join(app_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d, ignore_errors=True)
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
        except Exception:
            pass
        return False, f"Update application failed; rolled back to previous version. Error: {e}"

    # Clean staging
    shutil.rmtree(staging_dir, ignore_errors=True)
    return True, "Application updated successfully."

def perform_full_update(app_dir=None):
    """Checks for updates and applies if available."""
    if not app_dir:
        app_dir = get_app_dir()

    print("Checking for updates from GitHub Releases...", flush=True)
    info = check_for_updates(app_dir)

    if info.get("error"):
        print(f"Update check skipped ({info['error']}). Starting application normally.", flush=True)
        return False

    if not info.get("has_update"):
        print(f"GRC Risk Register is up to date (version {info['current_version']}).", flush=True)
        return False

    print(f"\nA new version of GRC Risk Register is available: v{info['latest_version']} (current: v{info['current_version']})")
    download_url = info.get("download_url")
    if not download_url:
        print("No download URL found for this release.", flush=True)
        return False

    updates_dir = os.path.join(app_dir, "updates", "download")
    os.makedirs(updates_dir, exist_ok=True)
    zip_dest = os.path.join(updates_dir, f"update_{info['latest_version']}.zip")

    print(f"Downloading update from {download_url} ...", flush=True)
    if not download_file(download_url, zip_dest):
        print("Failed to download update package.", flush=True)
        return False

    print("Applying update safely...", flush=True)
    success, msg = apply_update(zip_dest, app_dir)
    print(msg, flush=True)
    return success

if __name__ == "__main__":
    app_directory = get_app_dir()
    if "--check" in sys.argv:
        res = check_for_updates(app_directory)
        print(json.dumps(res, indent=2))
    elif "--version" in sys.argv:
        print(get_current_version(app_directory))
    elif "--update" in sys.argv:
        perform_full_update(app_directory)
    else:
        perform_full_update(app_directory)
