import hashlib
import random
import time as _time
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import JWT_SECRET, JWT_ALG
from .database import get_db
from .models import User

ACCESS_TTL_MIN = 60 * 24
REFRESH_TTL_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
_codes: dict = {}


def hash_password(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()


def verify_password(p: str, h: str) -> bool:
    return hash_password(p) == h


def make_code(phone: str) -> str:
    code = f"{random.randint(1000, 9999)}"
    _codes[phone] = (code, _time.time() + 300)
    return code


def check_code(phone: str, code: str) -> bool:
    entry = _codes.get(phone)
    if not entry:
        return False
    c, exp = entry
    return c == code and _time.time() < exp


def create_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "type": "access",
               "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TTL_MIN)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_refresh_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "type": "refresh",
               "exp": datetime.utcnow() + timedelta(days=REFRESH_TTL_DAYS)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_refresh_token(token: str) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        if payload.get("type") != "refresh":
            raise ValueError("not refresh")
        return int(payload["sub"])
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            "Invalid refresh token")


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        if payload.get("type") != "access":
            raise ValueError("not access")
        uid = int(payload["sub"])
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    user = db.get(User, uid)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def require_role(*roles: str):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if roles and user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
        return user
    return _dep