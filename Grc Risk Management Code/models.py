"""
GRC Risk Register - Data Models & Schema Validators
Provides structured schemas and validation methods for entities.
"""

from typing import Dict, Any, Optional, List
import re
from datetime import datetime
from risk_calculator import calculate_risk

VALID_ASSET_TYPES = ["Data", "System", "Device", "Service"]
VALID_IMPORTANCE_LEVELS = ["Low", "Medium", "High"]
VALID_RISK_STATUSES = ["Open", "In Progress", "Treated", "Closed"]
VALID_ROLES = ["admin", "analyst", "demo"]



class ValidationError(Exception):
    """Raised when an entity fails validation."""
    pass


def validate_user_payload(data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
    """Validates user creation/update payload."""
    cleaned = {}
    
    if not is_update or "username" in data:
        username = str(data.get("username", "")).strip()
        if not username or len(username) < 3 or len(username) > 32:
            raise ValidationError("Username must be between 3 and 32 characters.")
        if not re.match(r"^[a-zA-Z0-9_\-]+$", username):
            raise ValidationError("Username may only contain letters, numbers, underscores, and hyphens.")
        cleaned["username"] = username.lower()

    if not is_update or "password" in data:
        password = str(data.get("password", ""))
        if not is_update and not password:
            raise ValidationError("Password is required.")
        if password and len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.")
        if password:
            cleaned["password"] = password

    if not is_update or "role" in data:
        role = str(data.get("role", "analyst")).strip().lower()
        if role not in VALID_ROLES:
            raise ValidationError(f"Role must be one of: {', '.join(VALID_ROLES)}")
        cleaned["role"] = role

    if "full_name" in data or not is_update:
        full_name = str(data.get("full_name", "")).strip()
        cleaned["full_name"] = full_name or cleaned.get("username", "User")

    if "email" in data or not is_update:
        email = str(data.get("email", "")).strip()
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("Invalid email address format.")
        cleaned["email"] = email

    return cleaned


def validate_asset_payload(data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
    """Validates asset payload."""
    cleaned = {}

    if not is_update or "name" in data:
        name = str(data.get("name", "")).strip()
        if not name or len(name) < 2 or len(name) > 120:
            raise ValidationError("Asset Name is required and must be between 2 and 120 characters.")
        cleaned["name"] = name

    if "description" in data or not is_update:
        cleaned["description"] = str(data.get("description", "")).strip()

    if not is_update or "type" in data:
        asset_type = str(data.get("type", "Data")).strip()
        # Case-insensitive matching
        matched_type = next((t for t in VALID_ASSET_TYPES if t.lower() == asset_type.lower()), None)
        if not matched_type:
            raise ValidationError(f"Asset Type must be one of: {', '.join(VALID_ASSET_TYPES)}")
        cleaned["type"] = matched_type

    if not is_update or "owner" in data:
        owner = str(data.get("owner", "")).strip()
        if not owner or len(owner) < 2 or len(owner) > 80:
            raise ValidationError("Asset Owner is required (2 to 80 characters).")
        cleaned["owner"] = owner

    if not is_update or "importance" in data:
        importance = str(data.get("importance", "Medium")).strip()
        matched_imp = next((i for i in VALID_IMPORTANCE_LEVELS if i.lower() == importance.lower()), None)
        if not matched_imp:
            raise ValidationError(f"Importance must be one of: {', '.join(VALID_IMPORTANCE_LEVELS)}")
        cleaned["importance"] = matched_imp

    if "active" in data:
        cleaned["active"] = 1 if bool(data.get("active", True)) else 0

    return cleaned


def validate_risk_payload(data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
    """Validates risk payload and recalculates deterministic score/level."""
    cleaned = {}

    if not is_update or "title" in data:
        title = str(data.get("title", "")).strip()
        if not title or len(title) < 3 or len(title) > 150:
            raise ValidationError("Risk Title is required (3 to 150 characters).")
        cleaned["title"] = title

    if "description" in data or not is_update:
        cleaned["description"] = str(data.get("description", "")).strip()

    if "consequence" in data or not is_update:
        consequence = str(data.get("consequence", "")).strip()
        if not consequence and not is_update:
            raise ValidationError("Consequence / Potential Impact description is required.")
        cleaned["consequence"] = consequence

    if not is_update or "asset_id" in data:
        asset_id = data.get("asset_id")
        if not asset_id:
            raise ValidationError("A valid linked Asset is required.")
        try:
            cleaned["asset_id"] = int(asset_id)
        except (ValueError, TypeError):
            raise ValidationError("Asset ID must be a valid integer.")

    if not is_update or "likelihood" in data or "impact" in data:
        # If updating, default to existing if omitted in partial update handled in DB layer
        l_val = data.get("likelihood")
        i_val = data.get("impact")
        
        if l_val is not None:
            try:
                cleaned["likelihood"] = int(l_val)
            except (ValueError, TypeError):
                raise ValidationError("Likelihood must be an integer (1, 2, or 3).")
        
        if i_val is not None:
            try:
                cleaned["impact"] = int(i_val)
            except (ValueError, TypeError):
                raise ValidationError("Impact must be an integer (1, 2, or 3).")

        # If both are present, calculate score and level
        if "likelihood" in cleaned and "impact" in cleaned:
            calc = calculate_risk(cleaned["likelihood"], cleaned["impact"])
            cleaned["score"] = calc["score"]
            cleaned["level"] = calc["level"]

    if not is_update or "owner" in data:
        owner = str(data.get("owner", "")).strip()
        if not owner or len(owner) < 2 or len(owner) > 80:
            raise ValidationError("Risk Owner is required (2 to 80 characters).")
        cleaned["owner"] = owner

    if not is_update or "status" in data:
        status = str(data.get("status", "Open")).strip()
        matched_st = next((s for s in VALID_RISK_STATUSES if s.lower() == status.lower()), None)
        if not matched_st:
            raise ValidationError(f"Status must be one of: {', '.join(VALID_RISK_STATUSES)}")
        cleaned["status"] = matched_st

    if "notes" in data or not is_update:
        cleaned["notes"] = str(data.get("notes", "")).strip()

    if "active" in data:
        cleaned["active"] = 1 if bool(data.get("active", True)) else 0

    return cleaned
