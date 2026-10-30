"""
TASK-047: Role-Based Access Control (RBAC) Middleware & Token Validation
=========================================================================
Stage: Cross-Cutting / Security
Objective: Enforce role-based access restrictions across public, dispatcher,
           field lead, and administrator endpoints using signed tokens.

Roles:
- Public: Allowed on /reports (create), /reports/track/{id}, /health/*
- Dispatcher: Allowed on /reports/{id}/override, /clusters/{id}/action-brief, /reports/{id}/assign
- Field Lead: Restricted to departmental work orders and resolution
- Platform Admin: Full administrative privileges
"""

import hmac
import hashlib
import base64
import json
import time
import os
from typing import Optional, Dict, Any, List

JWT_SECRET = os.getenv("JWT_SECRET", "citysense-dev-secret-key-32chars-min!!").encode("utf-8")

# Recognized Roles in CitySense
ROLE_PUBLIC = "Public"
ROLE_DISPATCHER = "Dispatcher"
ROLE_FIELD_LEAD = "Field Lead"
ROLE_PLATFORM_ADMIN = "Platform Admin"

ALL_ROLES = [ROLE_PUBLIC, ROLE_DISPATCHER, ROLE_FIELD_LEAD, ROLE_PLATFORM_ADMIN]


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_decode(data_str: str) -> bytes:
    padding = "=" * (4 - len(data_str) % 4)
    return base64.urlsafe_b64decode(data_str + padding)


def create_access_token(
    user_id: str,
    role: str,
    department: Optional[str] = None,
    expires_in_seconds: int = 86400
) -> str:
    """
    Creates an HMAC-SHA256 signed JWT-style token containing user identity and role.
    Uses Python standard library for 100% portable reliability.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "role": role,
        "department": department,
        "iat": int(time.time()),
        "exp": int(time.time()) + expires_in_seconds
    }

    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    encoded_header = _b64_encode(header_bytes)
    encoded_payload = _b64_encode(payload_bytes)

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    signature = hmac.new(JWT_SECRET, signing_input, hashlib.sha256).digest()
    encoded_signature = _b64_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verifies token signature and expiration.
    Returns payload dictionary if valid, or raises ValueError.
    """
    if not token or not isinstance(token, str):
        raise ValueError("Token is required.")

    parts = token.strip().split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format.")

    encoded_header, encoded_payload, encoded_signature = parts

    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
    expected_sig = hmac.new(JWT_SECRET, signing_input, hashlib.sha256).digest()
    actual_sig = _b64_decode(encoded_signature)

    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("Invalid token signature.")

    payload = json.loads(_b64_decode(encoded_payload).decode("utf-8"))

    if payload.get("exp") and time.time() > payload["exp"]:
        raise ValueError("Token has expired.")

    return payload


def authenticate_request_token(auth_header: Optional[str], allowed_roles: List[str]) -> Dict[str, Any]:
    """
    Authenticates authorization header and validates role.
    Returns payload dict or raises:
      - PermissionError(401, "Unauthorized: Missing or invalid token.")
      - PermissionError(403, "Forbidden: Insufficient privileges.")
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        err = PermissionError("Unauthorized: Missing or invalid token.")
        err.status_code = 401
        raise err

    token = auth_header[7:].strip()
    try:
        payload = verify_access_token(token)
    except Exception as e:
        err = PermissionError(f"Unauthorized: {str(e)}")
        err.status_code = 401
        raise err

    role = payload.get("role")
    # Platform Admin always passes
    if role == ROLE_PLATFORM_ADMIN or role in allowed_roles:
        return payload

    err = PermissionError(f"Forbidden: Role '{role}' is not authorized for this operation.")
    err.status_code = 403
    raise err

