"""Persistent authentication and signed bearer token service."""

import base64
import hashlib
import hmac
import json
import os
import time
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.auth import Principal, Role
from src.infrastructure.database.models import UserModel


class AuthenticationError(Exception):
    pass


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations, salt_b64, digest_b64 = encoded.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(digest_b64.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


class AuthService:
    def __init__(self, session: Session, secret: str) -> None:
        if len(secret) < 32:
            raise ValueError("AUTH_SECRET must contain at least 32 characters")
        self.session, self.secret = session, secret.encode()

    def create_user(self, *, tenant_id: str, store_id: str, username: str, password: str, roles: set[Role]) -> UserModel:
        user = UserModel(id=str(uuid4()), tenant_id=tenant_id, store_id=store_id, username=username, password_hash=hash_password(password), roles=",".join(sorted(r.value for r in roles)), active=True)
        self.session.add(user)
        self.session.flush()
        return user

    def login(self, *, tenant_id: str, username: str, password: str, ttl_seconds: int = 3600) -> str:
        user = self.session.scalar(select(UserModel).where(UserModel.tenant_id == tenant_id, UserModel.username == username, UserModel.active.is_(True)))
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        payload = {"sub": user.id, "tenant": user.tenant_id, "store": user.store_id, "roles": user.roles.split(","), "exp": int(time.time()) + ttl_seconds}
        body = _b64(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
        signature = _b64(hmac.new(self.secret, body.encode(), hashlib.sha256).digest())
        return f"v1.{body}.{signature}"

    def authenticate(self, token: str) -> Principal:
        try:
            version, body, signature = token.split(".")
            if version != "v1" or not hmac.compare_digest(signature, _b64(hmac.new(self.secret, body.encode(), hashlib.sha256).digest())):
                raise AuthenticationError("Invalid token")
            payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
            if int(payload["exp"]) <= int(time.time()):
                raise AuthenticationError("Token expired")
            return Principal(payload["sub"], payload["tenant"], payload["store"], frozenset(Role(r) for r in payload["roles"]))
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise AuthenticationError("Invalid token") from exc
