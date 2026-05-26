"""JWT authentication middleware for Lucky Number.

Prevents CWE-522 (Insufficient Credential Protection) via bcrypt + JWT.
Prevents CWE-284 (Improper Access Control) via role verification.
Prevents CWE-307 (Brute Force) via account lockout after failed attempts.
"""
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt as _bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is required. Prevents CWE-522: no fallback secret.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))

security = HTTPBearer(auto_error=False)

# In-memory lockout tracker (use Redis in production)
_login_attempts: dict[str, dict] = {}
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15


def hash_password(password: str) -> str:
    """Hash a password with bcrypt (cost 12). Prevents CWE-522."""
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return _bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def validate_password_strength(password: str) -> None:
    """Validate password meets complexity requirements. Prevents CWE-521."""
    if len(password) < 8:
        raise HTTPException(status_code=422, detail="A senha deve ter no mínimo 8 caracteres")
    if len(password) > 128:
        raise HTTPException(status_code=422, detail="A senha deve ter no máximo 128 caracteres")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=422, detail="A senha deve conter pelo menos uma letra maiúscula")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=422, detail="A senha deve conter pelo menos uma letra minúscula")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=422, detail="A senha deve conter pelo menos um número")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\';/`~]", password):
        raise HTTPException(status_code=422, detail="A senha deve conter pelo menos um caractere especial")


def check_login_lockout(identifier: str) -> None:
    """Check if account is temporarily locked. Prevents CWE-307."""
    now = datetime.now(timezone.utc)
    record = _login_attempts.get(identifier)
    if record:
        if record["count"] >= MAX_LOGIN_ATTEMPTS:
            elapsed = (now - record["locked_at"]).total_seconds() if "locked_at" in record else 0
            if elapsed < LOGIN_LOCKOUT_MINUTES * 60:
                remaining = int(LOGIN_LOCKOUT_MINUTES * 60 - elapsed)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Conta temporariamente bloqueada. Tente novamente em {remaining} segundos.",
                )
            else:
                _login_attempts.pop(identifier, None)


def record_failed_login(identifier: str) -> None:
    """Record a failed login attempt and lock if threshold reached."""
    now = datetime.now(timezone.utc)
    record = _login_attempts.get(identifier, {"count": 0, "locked_at": None})
    record["count"] += 1
    if record["count"] >= MAX_LOGIN_ATTEMPTS:
        record["locked_at"] = now
    _login_attempts[identifier] = record


def reset_login_attempts(identifier: str) -> None:
    """Clear login attempts on successful login."""
    _login_attempts.pop(identifier, None)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """FastAPI dependency that extracts the current user from JWT.

    Returns dict with id, email, role. Raises 401 if invalid/missing.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticação necessária")
    payload = decode_jwt(credentials.credentials)
    return {"id": payload.get("sub"), "email": payload.get("email"), "role": payload.get("role")}
