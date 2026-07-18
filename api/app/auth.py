# === api/app/auth.py — JWT Authentication and RBAC ===

import os
from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

# ── Config ─────────────────────────────────────────────────────────────────
SECRET_KEY   = os.getenv("JWT_SECRET_KEY", "CHANGE-ME-IN-PRODUCTION-USE-ENV-VAR")
ALGORITHM    = "HS256"
EXPIRE_MINS  = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

security = HTTPBearer()


# ── Pydantic models ────────────────────────────────────────────────────────
class UserLogin(BaseModel):
    username: str
    password: str
    model_config = {"extra": "forbid"}


class Token(BaseModel):
    access_token: str
    token_type:   str


# ── Password verification ─────────────────────────────────────────────────
def verify_password(plain: str, stored: str) -> bool:
    """
    In production: use bcrypt (passlib).
    For demo: direct comparison with demo credentials.
    """
    return plain == stored


# ── JWT creation ───────────────────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    """Create a signed JWT with 30-minute expiry."""
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINS)
    payload["iat"] = datetime.now(timezone.utc)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ── JWT decoding ───────────────────────────────────────────────────────────
def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises 401 on any failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalid or expired: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Dependency: get current user ───────────────────────────────────────────
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """FastAPI dependency — extract and validate JWT from Authorization header."""
    return decode_token(credentials.credentials)


# ── Dependency factory: require specific roles ────────────────────────────
def require_role(allowed_roles: List[str]):
    """
    Returns a FastAPI dependency that enforces role-based access control.
    Usage: Depends(require_role(["admin", "engineer"]))
    """
    async def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        payload = decode_token(credentials.credentials)
        user_role = payload.get("role", "")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied. "
                    f"Your role '{user_role}' is not in allowed roles: {allowed_roles}"
                ),
            )
        return payload

    return role_checker
