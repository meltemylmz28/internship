from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


class Role(str):
    """Supported application roles for RBAC."""

    TEACHER = "teacher"
    SCHOOL_ADMIN = "school_admin"
    SYSTEM_ADMIN = "system_admin"


@dataclass(slots=True)
class AuthUser:
    username: str
    email: str
    password_hash: str
    role: str
    full_name: str
    created_at: int = field(default_factory=lambda: int(time.time()))

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "full_name": self.full_name,
            "created_at": self.created_at,
        }


class AuthService:
    """A lightweight authentication service with JWT-style signing and RBAC checks."""

    def __init__(self, secret_key: Optional[str] = None) -> None:
        self._secret_key = secret_key or os.getenv("AUTH_SECRET_KEY", "dev-secret-key")
        self._users: Dict[str, AuthUser] = {}

    def seed_demo_user(self) -> Dict[str, Any]:
        return self.register_user(
            username="demo.teacher",
            password="DemoPass123",
            email="demo.teacher@example.com",
            role=Role.TEACHER,
            full_name="Demo Öğretmen",
        )

    def register_user(
        self,
        *,
        username: str,
        password: str,
        email: str,
        role: str,
        full_name: str,
    ) -> Dict[str, Any]:
        if not username or not password or not email or not full_name:
            return {"success": False, "data": None, "error": "username, password, email and full_name are required"}

        if username in self._users:
            return {"success": False, "data": None, "error": "username already exists"}

        if role not in {Role.TEACHER, Role.SCHOOL_ADMIN, Role.SYSTEM_ADMIN}:
            return {"success": False, "data": None, "error": "invalid role"}

        hashed_password = self._hash_password(password)
        user = AuthUser(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role,
            full_name=full_name,
        )
        self._users[username] = user
        return {"success": True, "data": user.to_public_dict(), "error": None}

    def authenticate_user(self, username: str, password: str) -> Optional[AuthUser]:
        user = self._users.get(username)
        if user is None:
            return None
        if self._hash_password(password) != user.password_hash:
            return None
        return user

    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        user = self.authenticate_user(username, password)
        if user is None:
            return {"success": False, "data": None, "error": "invalid credentials"}

        token = self.create_token(user)
        return {
            "success": True,
            "data": {"token": token, "user": user.to_public_dict()},
            "error": None,
        }

    def create_token(self, user: AuthUser) -> str:
        now = int(time.time())
        payload = {
            "sub": user.username,
            "role": user.role,
            "email": user.email,
            "full_name": user.full_name,
            "iat": now,
            "exp": now + 3600,
        }
        return self._sign_jwt(payload)

    def decode_token(self, token: str) -> Dict[str, Any]:
        header_b64, payload_b64, signature = token.split(".")
        expected_signature = self._sign_signature(f"{header_b64}.{payload_b64}")
        if not hmac.compare_digest(expected_signature, signature):
            raise ValueError("invalid token signature")

        payload = json.loads(self._decode_base64url(payload_b64))
        if payload.get("exp", 0) < int(time.time()):
            raise ValueError("token expired")
        return payload

    def register_user_endpoint(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self.register_user(
            username=str(payload.get("username", "")).strip(),
            password=str(payload.get("password", "")).strip(),
            email=str(payload.get("email", "")).strip(),
            role=str(payload.get("role", Role.TEACHER)).strip(),
            full_name=str(payload.get("full_name", "")).strip(),
        )

    def login_user_endpoint(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        return self.login_user(
            username=str(payload.get("username", "")).strip(),
            password=str(payload.get("password", "")).strip(),
        )

    def _hash_password(self, password: str) -> str:
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), self._secret_key.encode("utf-8"), 200_000).hex()

    def _sign_jwt(self, payload: Dict[str, Any]) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = self._encode_base64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_b64 = self._encode_base64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signature = self._sign_signature(f"{header_b64}.{payload_b64}")
        return f"{header_b64}.{payload_b64}.{signature}"

    def _sign_signature(self, message: str) -> str:
        return self._encode_base64url(
            hmac.new(self._secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
        )

    @staticmethod
    def _encode_base64url(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")

    @staticmethod
    def _decode_base64url(value: str) -> str:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding).decode("utf-8")


def require_role(user: Optional[AuthUser], allowed_roles: List[str]) -> bool:
    if user is None:
        return False
    return user.role in allowed_roles
