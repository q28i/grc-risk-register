"""
GRC Risk Register - Authentication & Session Security Engine
Provides password hashing, session tokens, and role-based guards.
"""

import hashlib
import os
import secrets
import time
from typing import Dict, Optional, Tuple, Any

# In-memory active session store: session_token -> session_data
# session_data = {"user_id": int, "username": str, "role": str, "full_name": str, "expires_at": float}
_ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}
SESSION_LIFETIME_SECONDS = 86400  # 24 Hours


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hashes a password with PBKDF2-HMAC-SHA256 and salt."""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${key.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verifies a plaintext password against a stored salted hash."""
    try:
        salt, key_hex = hashed.split('$')
        recomputed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return secrets.compare_digest(recomputed.hex(), key_hex)
    except Exception:
        return False


def create_session(user: Dict[str, Any]) -> str:
    """Creates and registers a new secure session token."""
    token = secrets.token_urlsafe(32)
    _ACTIVE_SESSIONS[token] = {
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "full_name": user.get("full_name", user["username"]),
        "expires_at": time.time() + SESSION_LIFETIME_SECONDS
    }
    return token


def validate_session(token: Optional[str]) -> Optional[Dict[str, Any]]:
    """Validates an existing session token."""
    if not token or token not in _ACTIVE_SESSIONS:
        return None
    
    session = _ACTIVE_SESSIONS[token]
    if time.time() > session["expires_at"]:
        # Session expired
        del _ACTIVE_SESSIONS[token]
        return None
    
    return session


def revoke_session(token: Optional[str]) -> bool:
    """Revokes / logs out a session token."""
    if token and token in _ACTIVE_SESSIONS:
        del _ACTIVE_SESSIONS[token]
        return True
    return False


def clean_expired_sessions() -> int:
    """Purges expired sessions from memory."""
    now = time.time()
    expired_keys = [k for k, v in _ACTIVE_SESSIONS.items() if now > v["expires_at"]]
    for k in expired_keys:
        del _ACTIVE_SESSIONS[k]
    return len(expired_keys)
