"""
GRC Risk Register - Main Web Server & REST API
Built using Python Standard Library (http.server). Zero external pip dependencies.
"""

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import posixpath
import urllib.parse
import mimetypes
from typing import Dict, Any, Optional, Tuple

# Ensure graceful operation when launched detached or under pythonw without attached console
try:
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    else:
        sys.stdout.write("")
except Exception:
    sys.stdout = open(os.devnull, "w")

try:
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")
    else:
        sys.stderr.write("")
except Exception:
    sys.stderr = open(os.devnull, "w")

from database import (
    init_db, get_assets, get_asset_by_id, create_asset, update_asset, archive_asset, unarchive_asset,
    get_risks, get_risk_by_id, create_risk, update_risk, archive_risk, unarchive_risk,
    get_dashboard_metrics, get_user_by_username, get_user_by_id, get_all_users,
    get_audit_logs, log_event, DB_PATH,
    get_feature_controls, get_feature_controls_dict, is_feature_enabled_for_demo, update_feature_controls
)
from auth import (
    hash_password, verify_password, create_session, validate_session, revoke_session
)
from models import (
    validate_asset_payload, validate_risk_payload, validate_user_payload, ValidationError
)
from risk_calculator import get_matrix_definition, calculate_risk
from seed_data import seed_database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
HOST = "127.0.0.1"
PORT = 8000


class GRCRequestHandler(BaseHTTPRequestHandler):
    """Handles REST API requests and serves static assets."""

    server_version = "GRCRiskRegisterServer/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        """Safely logs messages without raising exceptions when detached."""
        try:
            super().log_message(format, *args)
        except Exception:
            pass

    def send_json_response(self, status_code: int, data: Any) -> None:
        """Sends a JSON response with standard security and CORS headers."""
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.end_headers()
        self.wfile.write(payload)

    def send_error_json(self, status_code: int, message: str) -> None:
        """Sends a standardized error JSON payload."""
        self.send_json_response(status_code, {"error": message, "status": status_code})

    def do_OPTIONS(self) -> None:
        """Handles CORS preflight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.end_headers()

    def get_auth_session(self) -> Optional[Dict[str, Any]]:
        """Extracts and validates session token from Authorization header or cookie."""
        auth_header = self.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        
        if not token:
            cookie_header = self.headers.get("Cookie", "")
            if "grc_session=" in cookie_header:
                for item in cookie_header.split(";"):
                    if item.strip().startswith("grc_session="):
                        token = item.strip().split("=")[1]
                        break

        if not token:
            return None

        return validate_session(token)

    def read_json_body(self) -> Dict[str, Any]:
        """Reads and parses incoming JSON request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw_body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON payload.")

    # ------------------------------------------------------------------
    # GET ROUTING
    # ------------------------------------------------------------------
    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # 1. API Routes
        if path.startswith("/api/"):
            self.handle_api_get(path, query)
            return

        # 2. HTML Templates
        if path in ("/", "/index.html", "/dashboard", "/assets", "/risks", "/reports", "/profile", "/matrix"):
            self.serve_file(os.path.join(TEMPLATES_DIR, "index.html"), "text/html; charset=utf-8")
            return

        # 3. Static Files
        if path.startswith("/static/"):
            relative_path = path[8:]  # strip /static/
            safe_path = posixpath.normpath(relative_path).lstrip('/')
            full_path = os.path.join(STATIC_DIR, safe_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                mime, _ = mimetypes.guess_type(full_path)
                self.serve_file(full_path, mime or "application/octet-stream")
                return

        # 4. Fallback 404
        self.send_error_json(404, f"Resource '{path}' not found.")

    def handle_api_get(self, path: str, query: Dict[str, list]) -> None:
        """Handles API GET endpoints."""
        session = self.get_auth_session()

        # Public / Auth info
        if path == "/api/auth/me":
            if not session:
                self.send_error_json(401, "Not authenticated.")
                return
            self.send_json_response(200, {"authenticated": True, "user": session})
            return

        if path == "/api/matrix-definition":
            self.send_json_response(200, get_matrix_definition())
            return

        # Feature Controls (Accessible to determine UI state)
        if path == "/api/feature-controls":
            controls = get_feature_controls()
            controls_dict = get_feature_controls_dict()
            self.send_json_response(200, {"controls": controls, "controls_dict": controls_dict})
            return

        # Protected Endpoints - Require Authentication
        if not session:
            self.send_error_json(401, "Authentication required to access this resource.")
            return

        # Dashboard Metrics
        if path == "/api/dashboard":
            metrics = get_dashboard_metrics()
            self.send_json_response(200, metrics)
            return

        # Assets
        if path == "/api/assets":
            active_only = query.get("active_only", ["true"])[0].lower() == "true"
            search = query.get("search", [None])[0]
            asset_type = query.get("type", [None])[0]
            assets = get_assets(active_only=active_only, search=search, asset_type=asset_type)
            self.send_json_response(200, assets)
            return

        if path.startswith("/api/assets/"):
            try:
                asset_id = int(path.split("/")[3])
                asset = get_asset_by_id(asset_id)
                if not asset:
                    self.send_error_json(404, f"Asset ID {asset_id} not found.")
                    return
                self.send_json_response(200, asset)
                return
            except ValueError:
                self.send_error_json(400, "Invalid Asset ID.")
                return

        # Risks
        if path == "/api/risks":
            active_only = query.get("active_only", ["true"])[0].lower() == "true"
            search = query.get("search", [None])[0]
            level = query.get("level", [None])[0]
            status = query.get("status", [None])[0]
            asset_id = query.get("asset_id", [None])[0]
            if asset_id:
                try:
                    asset_id = int(asset_id)
                except ValueError:
                    asset_id = None

            risks = get_risks(active_only=active_only, search=search, level=level, status=status, asset_id=asset_id)
            self.send_json_response(200, risks)
            return

        if path.startswith("/api/risks/"):
            try:
                risk_id = int(path.split("/")[3])
                risk = get_risk_by_id(risk_id)
                if not risk:
                    self.send_error_json(404, f"Risk ID {risk_id} not found.")
                    return
                self.send_json_response(200, risk)
                return
            except ValueError:
                self.send_error_json(400, "Invalid Risk ID.")
                return

        # User List (Admin Only)
        if path == "/api/users":
            if session["role"] != "admin":
                self.send_error_json(403, "Forbidden. Administrator role required.")
                return
            users = get_all_users()
            self.send_json_response(200, users)
            return

        # Audit Logs (Admin Only)
        if path == "/api/audit-logs":
            if session["role"] != "admin":
                self.send_error_json(403, "Forbidden. Administrator role required.")
                return
            logs = get_audit_logs(limit=100)
            self.send_json_response(200, logs)
            return

        self.send_error_json(404, f"API endpoint '{path}' not found.")

    # ------------------------------------------------------------------
    # POST ROUTING
    # ------------------------------------------------------------------
    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        try:
            body = self.read_json_body()
        except ValidationError as e:
            self.send_error_json(400, str(e))
            return

        # Auth Login
        if path == "/api/auth/login":
            username = str(body.get("username", "")).strip().lower()
            password = str(body.get("password", ""))

            user = get_user_by_username(username)
            if not user or not verify_password(password, user["password_hash"]):
                log_event("LOGIN_FAILED", "AUTH", username, "Failed login attempt (invalid credentials).")
                self.send_error_json(401, "Invalid username or password.")
                return

            token = create_session(user)
            log_event("LOGIN_SUCCESS", "AUTH", username, "User successfully logged in.",
                      user_id=user["id"], username=user["username"])
            
            self.send_json_response(200, {
                "success": True,
                "token": token,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "role": user["role"],
                    "full_name": user["full_name"],
                    "email": user["email"]
                }
            })
            return

        # Auth Logout
        if path == "/api/auth/logout":
            token = body.get("token") or self.headers.get("Authorization", "")[7:].strip()
            session = validate_session(token)
            if session:
                log_event("LOGOUT", "AUTH", session["username"], "User logged out.",
                          user_id=session["user_id"], username=session["username"])
                revoke_session(token)
            self.send_json_response(200, {"success": True, "message": "Logged out successfully."})
            return

        # Protected Endpoints
        session = self.get_auth_session()
        if not session:
            self.send_error_json(401, "Authentication required to perform this action.")
            return

        # Asset Creation
        if path == "/api/assets":
            if session["role"] == "demo" and not is_feature_enabled_for_demo("asset_add"):
                self.send_error_json(403, "This feature is currently under development.")
                return
            try:
                validated = validate_asset_payload(body, is_update=False)
                created = create_asset(validated, user_id=session["user_id"], username=session["username"])
                self.send_json_response(201, created)
                return
            except ValidationError as e:
                self.send_error_json(400, str(e))
                return
            except Exception as e:
                self.send_error_json(500, f"Error creating asset: {str(e)}")
                return

        # Asset Archiving / Unarchiving
        if path.startswith("/api/assets/") and path.endswith("/archive"):
            if session["role"] == "demo" and not is_feature_enabled_for_demo("asset_archive"):
                self.send_error_json(403, "This feature is currently under development.")
                return
            try:
                asset_id = int(path.split("/")[3])
                success = archive_asset(asset_id, user_id=session["user_id"], username=session["username"])
                if not success:
                    self.send_error_json(404, "Asset not found.")
                    return
                self.send_json_response(200, {"success": True, "message": "Asset archived successfully."})
                return
            except ValueError:
                self.send_error_json(400, "Invalid Asset ID.")
                return

        if path.startswith("/api/assets/") and path.endswith("/unarchive"):
            if session["role"] != "admin":
                self.send_error_json(403, "Only Administrators can restore archived assets.")
                return
            try:
                asset_id = int(path.split("/")[3])
                success = unarchive_asset(asset_id, user_id=session["user_id"], username=session["username"])
                if not success:
                    self.send_error_json(404, "Asset not found.")
                    return
                self.send_json_response(200, {"success": True, "message": "Asset restored successfully."})
                return
            except ValueError:
                self.send_error_json(400, "Invalid Asset ID.")
                return

        # Risk Creation
        if path == "/api/risks":
            if session["role"] == "demo" and not is_feature_enabled_for_demo("risk_add"):
                self.send_error_json(403, "This feature is currently under development.")
                return
            try:
                validated = validate_risk_payload(body, is_update=False)
                created = create_risk(validated, user_id=session["user_id"], username=session["username"])
                self.send_json_response(201, created)
                return
            except ValidationError as e:
                self.send_error_json(400, str(e))
                return
            except ValueError as e:
                self.send_error_json(400, str(e))
                return
            except Exception as e:
                self.send_error_json(500, f"Error creating risk: {str(e)}")
                return

        # Risk Archiving / Unarchiving
        if path.startswith("/api/risks/") and path.endswith("/archive"):
            if session["role"] == "demo" and not is_feature_enabled_for_demo("risk_archive"):
                self.send_error_json(403, "This feature is currently under development.")
                return
            try:
                risk_id = int(path.split("/")[3])
                success = archive_risk(risk_id, user_id=session["user_id"], username=session["username"])
                if not success:
                    self.send_error_json(404, "Risk not found.")
                    return
                self.send_json_response(200, {"success": True, "message": "Risk archived successfully."})
                return
            except ValueError:
                self.send_error_json(400, "Invalid Risk ID.")
                return

        if path.startswith("/api/risks/") and path.endswith("/unarchive"):
            if session["role"] != "admin":
                self.send_error_json(403, "Only Administrators can restore archived risks.")
                return
            try:
                risk_id = int(path.split("/")[3])
                success = unarchive_risk(risk_id, user_id=session["user_id"], username=session["username"])
                if not success:
                    self.send_error_json(404, "Risk not found.")
                    return
                self.send_json_response(200, {"success": True, "message": "Risk restored successfully."})
                return
            except ValueError:
                self.send_error_json(400, "Invalid Risk ID.")
                return

        self.send_error_json(404, f"POST endpoint '{path}' not found.")

    # ------------------------------------------------------------------
    # PUT ROUTING
    # ------------------------------------------------------------------
    def do_PUT(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        session = self.get_auth_session()
        if not session:
            self.send_error_json(401, "Authentication required.")
            return

        try:
            body = self.read_json_body()
        except ValidationError as e:
            self.send_error_json(400, str(e))
            return

        # Feature Controls Update (Admin Only)
        if path == "/api/feature-controls":
            if session["role"] != "admin":
                self.send_error_json(403, "Only Administrators can modify demo feature controls.")
                return
            controls = body.get("controls", {})
            if not isinstance(controls, dict):
                self.send_error_json(400, "Invalid controls payload.")
                return
            update_feature_controls(controls, user_id=session["user_id"], username=session["username"])
            self.send_json_response(200, {
                "success": True,
                "message": "Feature controls updated successfully.",
                "controls": get_feature_controls(),
                "controls_dict": get_feature_controls_dict()
            })
            return

        # Asset Update
        if path.startswith("/api/assets/"):
            if session["role"] == "demo" and not is_feature_enabled_for_demo("asset_edit"):
                self.send_error_json(403, "This feature is currently under development.")
                return
            try:
                asset_id = int(path.split("/")[3])
                validated = validate_asset_payload(body, is_update=True)
                updated = update_asset(asset_id, validated, user_id=session["user_id"], username=session["username"])
                if not updated:
                    self.send_error_json(404, "Asset not found.")
                    return
                self.send_json_response(200, updated)
                return
            except ValidationError as e:
                self.send_error_json(400, str(e))
                return
            except ValueError:
                self.send_error_json(400, "Invalid Asset ID.")
                return

        # Risk Update
        if path.startswith("/api/risks/"):
            if session["role"] == "demo":
                is_status_only = all(k in ("status", "notes") for k in body.keys())
                if is_status_only:
                    if not is_feature_enabled_for_demo("risk_status_change"):
                        self.send_error_json(403, "This feature is currently under development.")
                        return
                else:
                    if not is_feature_enabled_for_demo("risk_edit"):
                        self.send_error_json(403, "This feature is currently under development.")
                        return

            try:
                risk_id = int(path.split("/")[3])
                validated = validate_risk_payload(body, is_update=True)
                updated = update_risk(risk_id, validated, user_id=session["user_id"], username=session["username"])
                if not updated:
                    self.send_error_json(404, "Risk not found.")
                    return
                self.send_json_response(200, updated)
                return
            except ValidationError as e:
                self.send_error_json(400, str(e))
                return
            except ValueError:
                self.send_error_json(400, "Invalid Risk ID.")
                return

        self.send_error_json(404, f"PUT endpoint '{path}' not found.")

    def serve_file(self, filepath: str, content_type: str) -> None:
        """Serves a static file."""
        if not os.path.exists(filepath):
            self.send_error_json(404, "File not found.")
            return
        
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error_json(500, f"Error reading file: {str(e)}")


def run_server(port: int = PORT) -> None:
    """Initializes DB and runs the server."""
    print("[Server] Initializing GRC Risk Register database...")
    init_db()
    seed_database()
    
    server_address = (HOST, port)
    httpd = HTTPServer(server_address, GRCRequestHandler)
    print(f"\n=======================================================")
    print(f"  GRC RISK REGISTER - Web Application Active")
    print(f"  URL: http://{HOST}:{port}")
    print(f"  Default Accounts:")
    print(f"    - Administrator: admin / admin123")
    print(f"    - Risk Analyst:  analyst / analyst123")
    print(f"    - Demo User:     demo / demo123")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
