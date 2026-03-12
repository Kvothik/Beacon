from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any
from uuid import UUID
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.db import get_session
from backend.app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class ApiError(Exception):
    status_code: int
    code: str
    message: str
    details: Optional[dict[str, Any]] = None
    retryable: bool = False


@dataclass
class TokenPayload:
    sub: str
    exp: int


def get_bearer_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[str]:
    if credentials is None:
        return None
    return credentials.credentials


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt_hex, digest_hex = password_hash.split(":", 1)
    expected = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), 200000
    )
    return hmac.compare_digest(expected.hex(), digest_hex)


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_access_token(user_id: UUID) -> str:
    payload = {
        "sub": str(user_id),
        "exp": int(time.time()) + settings.auth_token_ttl_seconds,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_segment = _b64encode(payload_bytes)
    signature = hmac.new(
        settings.auth_secret.encode("utf-8"), payload_segment.encode("utf-8"), hashlib.sha256
    ).digest()
    return f"{payload_segment}.{_b64encode(signature)}"


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload_segment, signature_segment = token.split(".", 1)
    except ValueError as exc:
        raise ApiError(401, "auth_unauthorized", "Authentication is required.") from exc

    expected_signature = hmac.new(
        settings.auth_secret.encode("utf-8"), payload_segment.encode("utf-8"), hashlib.sha256
    ).digest()
    actual_signature = _b64decode(signature_segment)
    if not hmac.compare_digest(expected_signature, actual_signature):
        raise ApiError(401, "auth_unauthorized", "Authentication is required.")

    payload = json.loads(_b64decode(payload_segment))
    if payload["exp"] < int(time.time()):
        raise ApiError(401, "auth_token_expired", "Authentication token has expired.")
    return TokenPayload(sub=payload["sub"], exp=payload["exp"])


def require_authenticated_user(
    token: Optional[str] = Depends(get_bearer_token),
    session: Session = Depends(get_session),
) -> User:
    if not token:
        raise ApiError(401, "auth_unauthorized", "Authentication is required.")

    payload = decode_access_token(token)
    user = session.scalar(select(User).where(User.id == UUID(payload.sub)))
    if user is None:
        raise ApiError(401, "auth_unauthorized", "Authentication is required.")
    return user
