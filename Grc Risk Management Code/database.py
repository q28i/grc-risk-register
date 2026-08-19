"""
GRC Risk Register - Database & Persistence Engine
SQLite transactional storage with automatic schema migration, indexing, and seed initialization.
"""

import sqlite3
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from auth import hash_password
from risk_calculator import calculate_risk

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grc_risk_register.db")


def get_db_path(db_path: Optional[str] = None) -> str:
    """Returns the provided db_path or the current module-level DB_PATH."""
    return db_path if db_path is not None else DB_PATH


def get_utc_timestamp() -> str:
    """Returns an ISO-8601 formatted UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Returns a SQLite connection with Row factory and Foreign Key enforcement."""
    path = get_db_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


DEFAULT_FEATURE_CONTROLS = [
    # (feature_key, label, category, description, enabled_for_demo)
    # 1. Dashboard
    ("dashboard_view", "View Dashboard", "Dashboard", "Access and view the executive dashboard overview", 1),
    ("dashboard_refresh", "Refresh Dashboard", "Dashboard", "Trigger executive dashboard metric reload", 1),
    ("dashboard_matrix_view", "View Risk Matrix", "Dashboard", "View the 3x3 qualitative risk matrix heatmap", 1),
    ("dashboard_distribution_view", "View Risk Distribution", "Dashboard", "View severity breakdown and treatment distribution", 1),
    ("dashboard_recent_view", "View Recent Risks", "Dashboard", "View recent cybersecurity risks list on dashboard", 1),

    # 2. Assets
    ("asset_view", "View Assets", "Assets", "View registered organizational asset inventory", 1),
    ("asset_search", "Search Assets", "Assets", "Execute asset inventory search queries", 1),
    ("asset_add", "Add Asset", "Assets", "Register new organizational assets", 1),
    ("asset_edit", "Edit Asset", "Assets", "Modify existing organizational assets", 0),
    ("asset_archive", "Archive Asset", "Assets", "Archive organizational assets", 0),
    ("asset_show_archived", "Show Archived Assets", "Assets", "Toggle archived assets visibility", 1),
    ("asset_filter", "Filter Assets", "Assets", "Filter assets by category and type", 1),

    # 3. Risks
    ("risk_view", "View Risks", "Risks", "View cybersecurity risk register", 1),
    ("risk_search", "Search Risks", "Risks", "Execute risk register search queries", 1),
    ("risk_add", "Add Risk", "Risks", "Identify and assess new cybersecurity risks", 1),
    ("risk_edit", "Edit Risk", "Risks", "Modify risk details, likelihood, and impact", 0),
    ("risk_archive", "Archive Risk", "Risks", "Archive cybersecurity risks", 0),
    ("risk_status_change", "Change Risk Status", "Risks", "Update risk treatment lifecycle status", 1),
    ("risk_show_archived", "Show Archived Risks", "Risks", "Toggle archived risks visibility", 1),
    ("risk_filter", "Filter Risks", "Risks", "Filter risks by severity level and status", 1),
    ("risk_view_details", "View Risk Details", "Risks", "View full threat scenario and consequence details", 1),

    # 4. Reports
    ("report_view", "View Reports", "Reports", "View executive risk summaries and printable reports", 1),
    ("report_print", "Print Report", "Reports", "Trigger browser print dialog for reports", 1),
    ("report_export_csv", "Export CSV", "Reports", "Download risk register dataset as CSV", 0),

    # 5. Profile / Audit
    ("profile_view", "View Profile", "Profile / Audit", "View active session profile and risk model reference", 1),
    ("audit_view", "View Audit Log", "Profile / Audit", "Inspect system audit traceability logs", 0),

    # 6. Administration
    ("admin_fc_view", "View Feature Controls", "Administration", "View administrator feature control configuration", 0),
    ("admin_fc_modify", "Modify Feature Controls", "Administration", "Modify feature availability settings", 0),
    ("admin_users_view", "View User Administration", "Administration", "View user accounts management list", 0),
]


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes database schema, default users (admin, analyst, demo), and feature controls."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'analyst', 'demo')),
        full_name TEXT NOT NULL,
        email TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # Safe migration for existing databases with older CHECK constraints
    user_table_sql = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
    if user_table_sql and "'demo'" not in user_table_sql[0]:
        cursor.execute("CREATE TABLE users_migrated (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin', 'analyst', 'demo')), full_name TEXT NOT NULL, email TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)")
        cursor.execute("INSERT INTO users_migrated SELECT id, username, password_hash, role, full_name, email, created_at, updated_at FROM users")
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_migrated RENAME TO users")
        conn.commit()


    # 2. Assets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        type TEXT NOT NULL CHECK(type IN ('Data', 'System', 'Device', 'Service')),
        owner TEXT NOT NULL,
        importance TEXT NOT NULL CHECK(importance IN ('Low', 'Medium', 'High')),
        active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_active ON assets(active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type)")

    # 3. Risks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        risk_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        consequence TEXT NOT NULL,
        asset_id INTEGER NOT NULL,
        likelihood INTEGER NOT NULL CHECK(likelihood BETWEEN 1 AND 3),
        impact INTEGER NOT NULL CHECK(impact BETWEEN 1 AND 3),
        score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 9),
        level TEXT NOT NULL CHECK(level IN ('Low', 'Medium', 'High')),
        owner TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('Open', 'In Progress', 'Treated', 'Closed')),
        notes TEXT,
        active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (asset_id) REFERENCES assets (id) ON DELETE RESTRICT
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_risks_active ON risks(active)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_risks_level ON risks(level)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_risks_status ON risks(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_risks_asset ON risks(asset_id)")

    # 4. Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_id INTEGER,
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT,
        details TEXT
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)")

    # 5. Feature Controls Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feature_controls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feature_key TEXT UNIQUE NOT NULL,
        label TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        enabled_for_demo INTEGER NOT NULL DEFAULT 1 CHECK(enabled_for_demo IN (0, 1)),
        updated_at TEXT NOT NULL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fc_key ON feature_controls(feature_key)")

    conn.commit()

    # Pre-seed standard accounts
    now = get_utc_timestamp()
    admin_hash = hash_password("admin123")
    analyst_hash = hash_password("analyst123")
    demo_hash = hash_password("demo123")

    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name, email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("admin", admin_hash, "admin", "System Administrator", "admin@organization.local", now, now))

    cursor.execute("SELECT id FROM users WHERE username = 'analyst'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name, email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("analyst", analyst_hash, "analyst", "Cybersecurity Risk Analyst", "analyst@organization.local", now, now))

    cursor.execute("SELECT id FROM users WHERE username = 'demo'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, password_hash, role, full_name, email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("demo", demo_hash, "demo", "Demo User", "demo@organization.local", now, now))

    # Pre-seed default feature controls (insert new or update metadata, preserving user settings)
    for f_key, f_lbl, f_cat, f_desc, f_demo in DEFAULT_FEATURE_CONTROLS:
        cursor.execute("SELECT id FROM feature_controls WHERE feature_key = ?", (f_key,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO feature_controls (feature_key, label, category, description, enabled_for_demo, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (f_key, f_lbl, f_cat, f_desc, f_demo, now))
        else:
            cursor.execute("""
                UPDATE feature_controls
                SET label = ?, category = ?, description = ?
                WHERE feature_key = ?
            """, (f_lbl, f_cat, f_desc, f_key))

    conn.commit()
    conn.close()


# ----------------------------------------------------------------------
# FEATURE CONTROLS REPOSITORY
# ----------------------------------------------------------------------

def get_feature_controls(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all feature control records ordered by logical category priority and id."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        rows = conn.execute("""
            SELECT id, feature_key, label, label as feature_name, category, description, enabled_for_demo, enabled_for_demo as is_enabled_for_demo, updated_at
            FROM feature_controls
            ORDER BY 
                CASE category
                    WHEN 'Dashboard' THEN 1
                    WHEN 'Assets' THEN 2
                    WHEN 'Risks' THEN 3
                    WHEN 'Reports' THEN 4
                    WHEN 'Profile / Audit' THEN 5
                    WHEN 'Administration' THEN 6
                    ELSE 7
                END,
                id ASC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_feature_controls_dict(db_path: Optional[str] = None) -> Dict[str, bool]:
    """Returns a simple dictionary of {feature_key: bool}."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        rows = conn.execute("SELECT feature_key, enabled_for_demo FROM feature_controls").fetchall()
        return {r["feature_key"]: bool(r["enabled_for_demo"]) for r in rows}
    finally:
        conn.close()


def is_feature_enabled_for_demo(feature_key: str, db_path: Optional[str] = None) -> bool:
    """Checks if a specific feature is enabled for the demo user."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        row = conn.execute("SELECT enabled_for_demo FROM feature_controls WHERE feature_key = ?", (feature_key,)).fetchone()
        if row is None:
            return False
        return bool(row["enabled_for_demo"])
    finally:
        conn.close()


def update_feature_controls(controls: Dict[str, bool], user_id: Optional[int] = None, username: str = "system", db_path: Optional[str] = None) -> None:
    """Updates multiple feature control states in a single transaction."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        for key, enabled in controls.items():
            val = 1 if enabled else 0
            conn.execute("""
                UPDATE feature_controls
                SET enabled_for_demo = ?, updated_at = ?
                WHERE feature_key = ?
            """, (val, now, key))
        
        # Audit log
        conn.execute("""
            INSERT INTO audit_logs (timestamp, user_id, username, action, entity_type, entity_id, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (now, user_id, username, "UPDATE_FEATURE_CONTROLS", "CONFIG", "DEMO_CONTROLS", f"Updated {len(controls)} demo feature settings."))
        
        conn.commit()
    finally:
        conn.close()



# ----------------------------------------------------------------------
# AUDIT LOGGING
# ----------------------------------------------------------------------

def log_event(action: str, entity_type: str, entity_id: str, details: str,
              user_id: Optional[int] = None, username: str = "system", db_path: Optional[str] = None) -> None:
    """Records an audit event in the database."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        conn.execute("""
            INSERT INTO audit_logs (timestamp, user_id, username, action, entity_type, entity_id, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (now, user_id, username, action, entity_type, entity_id, details))
        conn.commit()
    finally:
        conn.close()


def get_audit_logs(limit: int = 100, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves recent audit logs."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        rows = conn.execute("""
            SELECT id, timestamp, user_id, username, action, entity_type, entity_id, details
            FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ----------------------------------------------------------------------
# USER REPOSITORY
# ----------------------------------------------------------------------

def get_user_by_username(username: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username.lower(),)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        row = conn.execute("SELECT id, username, role, full_name, email, created_at, updated_at FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_users(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        rows = conn.execute("SELECT id, username, role, full_name, email, created_at, updated_at FROM users ORDER BY id ASC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ----------------------------------------------------------------------
# ASSET REPOSITORY
# ----------------------------------------------------------------------

def get_next_asset_code(cursor: sqlite3.Cursor) -> str:
    """Generates the next sequential AST-xxx code."""
    cursor.execute("SELECT id FROM assets ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    next_id = (row[0] + 1) if row else 1
    return f"AST-{next_id:03d}"


def get_assets(active_only: bool = True, search: Optional[str] = None,
               asset_type: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        query = "SELECT * FROM assets WHERE 1=1"
        params = []

        if active_only:
            query += " AND active = 1"
        if asset_type:
            query += " AND type = ?"
            params.append(asset_type)
        if search:
            query += " AND (name LIKE ? OR asset_id LIKE ? OR description LIKE ? OR owner LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param, s_param, s_param])

        query += " ORDER BY id DESC"
        rows = conn.execute(query, params).fetchall()
        
        # Attach risk count for each asset
        result = []
        for r in rows:
            asset = dict(r)
            r_count = conn.execute("SELECT COUNT(*) FROM risks WHERE asset_id = ? AND active = 1", (asset["id"],)).fetchone()[0]
            asset["risk_count"] = r_count
            result.append(asset)
        return result
    finally:
        conn.close()


def get_asset_by_id(asset_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
        if not row:
            return None
        asset = dict(row)
        asset["risk_count"] = conn.execute("SELECT COUNT(*) FROM risks WHERE asset_id = ? AND active = 1", (asset["id"],)).fetchone()[0]
        return asset
    finally:
        conn.close()


def create_asset(data: Dict[str, Any], user_id: Optional[int] = None,
                 username: str = "system", db_path: Optional[str] = None) -> Dict[str, Any]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        cursor = conn.cursor()
        asset_code = get_next_asset_code(cursor)
        cursor.execute("""
            INSERT INTO assets (asset_id, name, description, type, owner, importance, active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset_code,
            data["name"],
            data.get("description", ""),
            data["type"],
            data["owner"],
            data["importance"],
            data.get("active", 1),
            now,
            now
        ))
        new_id = cursor.lastrowid
        conn.commit()

        log_event("CREATE", "ASSET", asset_code, f"Created asset '{data['name']}' ({data['type']}).",
                  user_id, username, db_path=path)

        return get_asset_by_id(new_id, db_path=path)
    finally:
        conn.close()


def update_asset(asset_id: int, data: Dict[str, Any], user_id: Optional[int] = None,
                 username: str = "system", db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        existing = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
        if not existing:
            return None

        fields = ["updated_at = ?"]
        params = [now]

        for k in ["name", "description", "type", "owner", "importance", "active"]:
            if k in data:
                fields.append(f"{k} = ?")
                params.append(data[k])

        params.append(asset_id)
        conn.execute(f"UPDATE assets SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()

        log_event("UPDATE", "ASSET", existing["asset_id"], f"Updated asset '{existing['asset_id']}'.",
                  user_id, username, db_path=path)

        return get_asset_by_id(asset_id, db_path=path)
    finally:
        conn.close()


def archive_asset(asset_id: int, user_id: Optional[int] = None,
                  username: str = "system", db_path: Optional[str] = None) -> bool:
    """Soft-archives an asset."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        existing = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
        if not existing:
            return False
        conn.execute("UPDATE assets SET active = 0, updated_at = ? WHERE id = ?", (now, asset_id))
        conn.commit()
        log_event("ARCHIVE", "ASSET", existing["asset_id"], f"Archived asset '{existing['name']}'.",
                  user_id, username, db_path=path)
        return True
    finally:
        conn.close()


def unarchive_asset(asset_id: int, user_id: Optional[int] = None,
                    username: str = "system", db_path: Optional[str] = None) -> bool:
    """Restores an archived asset."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        existing = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
        if not existing:
            return False
        conn.execute("UPDATE assets SET active = 1, updated_at = ? WHERE id = ?", (now, asset_id))
        conn.commit()
        log_event("UNARCHIVE", "ASSET", existing["asset_id"], f"Restored asset '{existing['name']}'.",
                  user_id, username, db_path=path)
        return True
    finally:
        conn.close()


# ----------------------------------------------------------------------
# RISK REPOSITORY
# ----------------------------------------------------------------------

def get_next_risk_code(cursor: sqlite3.Cursor) -> str:
    """Generates the next sequential RSK-xxx code."""
    cursor.execute("SELECT id FROM risks ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    next_id = (row[0] + 1) if row else 1
    return f"RSK-{next_id:03d}"


def get_risks(active_only: bool = True, search: Optional[str] = None,
              level: Optional[str] = None, status: Optional[str] = None,
              asset_id: Optional[int] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        query = """
            SELECT r.*, a.asset_id as asset_code, a.name as asset_name, a.type as asset_type
            FROM risks r
            JOIN assets a ON r.asset_id = a.id
            WHERE 1=1
        """
        params = []

        if active_only:
            query += " AND r.active = 1"
        if level:
            query += " AND r.level = ?"
            params.append(level)
        if status:
            query += " AND r.status = ?"
            params.append(status)
        if asset_id:
            query += " AND r.asset_id = ?"
            params.append(asset_id)
        if search:
            query += " AND (r.title LIKE ? OR r.risk_id LIKE ? OR r.description LIKE ? OR r.owner LIKE ? OR a.name LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param, s_param, s_param, s_param])

        query += " ORDER BY r.score DESC, r.id DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_risk_by_id(risk_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        row = conn.execute("""
            SELECT r.*, a.asset_id as asset_code, a.name as asset_name, a.type as asset_type
            FROM risks r
            JOIN assets a ON r.asset_id = a.id
            WHERE r.id = ?
        """, (risk_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_risk(data: Dict[str, Any], user_id: Optional[int] = None,
                username: str = "system", db_path: Optional[str] = None) -> Dict[str, Any]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        cursor = conn.cursor()
        
        # Verify asset exists
        asset = conn.execute("SELECT * FROM assets WHERE id = ?", (data["asset_id"],)).fetchone()
        if not asset:
            raise ValueError(f"Referenced Asset with ID {data['asset_id']} does not exist.")

        # Ensure calculation is fresh
        calc = calculate_risk(data["likelihood"], data["impact"])
        score = calc["score"]
        level = calc["level"]

        risk_code = get_next_risk_code(cursor)
        cursor.execute("""
            INSERT INTO risks (risk_id, title, description, consequence, asset_id,
                               likelihood, impact, score, level, owner, status, notes, active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            risk_code,
            data["title"],
            data.get("description", ""),
            data["consequence"],
            data["asset_id"],
            data["likelihood"],
            data["impact"],
            score,
            level,
            data["owner"],
            data.get("status", "Open"),
            data.get("notes", ""),
            data.get("active", 1),
            now,
            now
        ))
        new_id = cursor.lastrowid
        conn.commit()

        log_event("CREATE", "RISK", risk_code,
                  f"Created risk '{data['title']}' for asset '{asset['name']}' (Score: {score}, Level: {level}).",
                  user_id, username, db_path=path)

        return get_risk_by_id(new_id, db_path=path)
    finally:
        conn.close()


def update_risk(risk_id: int, data: Dict[str, Any], user_id: Optional[int] = None,
                username: str = "system", db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        existing = conn.execute("SELECT * FROM risks WHERE id = ?", (risk_id,)).fetchone()
        if not existing:
            return None

        # Determine likelihood & impact
        new_l = data.get("likelihood", existing["likelihood"])
        new_i = data.get("impact", existing["impact"])
        calc = calculate_risk(new_l, new_i)
        
        fields = [
            "updated_at = ?", "likelihood = ?", "impact = ?", "score = ?", "level = ?"
        ]
        params = [now, new_l, new_i, calc["score"], calc["level"]]

        for k in ["title", "description", "consequence", "asset_id", "owner", "status", "notes", "active"]:
            if k in data:
                fields.append(f"{k} = ?")
                params.append(data[k])

        params.append(risk_id)
        conn.execute(f"UPDATE risks SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()

        log_event("UPDATE", "RISK", existing["risk_id"],
                  f"Updated risk '{existing['risk_id']}' (Status: {data.get('status', existing['status'])}, Score: {calc['score']}).",
                  user_id, username, db_path=path)

        return get_risk_by_id(risk_id, db_path=path)
    finally:
        conn.close()


def archive_risk(risk_id: int, user_id: Optional[int] = None,
                 username: str = "system", db_path: Optional[str] = None) -> bool:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        existing = conn.execute("SELECT * FROM risks WHERE id = ?", (risk_id,)).fetchone()
        if not existing:
            return False
        conn.execute("UPDATE risks SET active = 0, updated_at = ? WHERE id = ?", (now, risk_id))
        conn.commit()
        log_event("ARCHIVE", "RISK", existing["risk_id"], f"Archived risk '{existing['title']}'.",
                  user_id, username, db_path=path)
        return True
    finally:
        conn.close()


def unarchive_risk(risk_id: int, user_id: Optional[int] = None,
                   username: str = "system", db_path: Optional[str] = None) -> bool:
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    now = get_utc_timestamp()
    try:
        existing = conn.execute("SELECT * FROM risks WHERE id = ?", (risk_id,)).fetchone()
        if not existing:
            return False
        conn.execute("UPDATE risks SET active = 1, updated_at = ? WHERE id = ?", (now, risk_id))
        conn.commit()
        log_event("UNARCHIVE", "RISK", existing["risk_id"], f"Restored risk '{existing['title']}'.",
                  user_id, username, db_path=path)
        return True
    finally:
        conn.close()


# ----------------------------------------------------------------------
# DASHBOARD METRICS AGGREGATION
# ----------------------------------------------------------------------

def get_dashboard_metrics(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Computes all summary cards, level breakdown, status counts, and 3x3 heatmap data."""
    path = get_db_path(db_path)
    conn = get_db_connection(path)
    try:
        total_assets = conn.execute("SELECT COUNT(*) FROM assets WHERE active = 1").fetchone()[0]
        total_risks = conn.execute("SELECT COUNT(*) FROM risks WHERE active = 1").fetchone()[0]
        open_risks = conn.execute("SELECT COUNT(*) FROM risks WHERE active = 1 AND status IN ('Open', 'In Progress')").fetchone()[0]
        high_risks = conn.execute("SELECT COUNT(*) FROM risks WHERE active = 1 AND level = 'High'").fetchone()[0]

        # By Risk Level
        level_counts = {"Low": 0, "Medium": 0, "High": 0}
        for row in conn.execute("SELECT level, COUNT(*) FROM risks WHERE active = 1 GROUP BY level").fetchall():
            if row[0] in level_counts:
                level_counts[row[0]] = row[1]

        # By Status
        status_counts = {"Open": 0, "In Progress": 0, "Treated": 0, "Closed": 0}
        for row in conn.execute("SELECT status, COUNT(*) FROM risks WHERE active = 1 GROUP BY status").fetchall():
            if row[0] in status_counts:
                status_counts[row[0]] = row[1]

        # By Asset Type
        asset_type_counts = {"Data": 0, "System": 0, "Device": 0, "Service": 0}
        for row in conn.execute("SELECT type, COUNT(*) FROM assets WHERE active = 1 GROUP BY type").fetchall():
            if row[0] in asset_type_counts:
                asset_type_counts[row[0]] = row[1]

        # 3x3 Heatmap Matrix Grid (Likelihood: 3 to 1 down, Impact: 1 to 3 across)
        heatmap_grid = []
        for l in [3, 2, 1]:  # High (3), Medium (2), Low (1)
            row = []
            for i in [1, 2, 3]:  # Low (1), Medium (2), High (3)
                count = conn.execute("""
                    SELECT COUNT(*) FROM risks
                    WHERE active = 1 AND likelihood = ? AND impact = ?
                """, (l, i)).fetchone()[0]
                calc = calculate_risk(l, i)
                row.append({
                    "likelihood": l,
                    "impact": i,
                    "score": calc["score"],
                    "level": calc["level"],
                    "count": count,
                    "color": calc["color"],
                    "bg_color": calc["bg_color"]
                })
            heatmap_grid.append(row)

        # Recent 5 risks
        recent_risks_rows = conn.execute("""
            SELECT r.id, r.risk_id, r.title, r.score, r.level, r.status, r.owner, a.name as asset_name
            FROM risks r
            JOIN assets a ON r.asset_id = a.id
            WHERE r.active = 1
            ORDER BY r.id DESC
            LIMIT 5
        """).fetchall()
        recent_risks = [dict(r) for r in recent_risks_rows]

        return {
            "summary": {
                "total_assets": total_assets,
                "total_risks": total_risks,
                "open_risks": open_risks,
                "high_risks": high_risks
            },
            "level_distribution": level_counts,
            "status_distribution": status_counts,
            "asset_type_distribution": asset_type_counts,
            "heatmap": heatmap_grid,
            "recent_risks": recent_risks
        }
    finally:
        conn.close()
