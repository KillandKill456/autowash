from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import (decode_refresh_token, create_token,
                    create_refresh_token)
from ..database import get_db
from ..dto.auth_dto import (LoginDTO, RefreshDTO, SendCodeDTO,
                            SendCodeResponseDTO, TokenDTO)
from ..models import User
from ..services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/code", response_model=SendCodeResponseDTO)
def send_code(dto: SendCodeDTO, db: Session = Depends(get_db)):
    return AuthService(db).send_code(dto.phone)


@router.post("/login", response_model=TokenDTO)
def login(dto: LoginDTO, db: Session = Depends(get_db)):
    return AuthService(db).login(dto)


@router.post("/refresh", response_model=TokenDTO)
def refresh(dto: RefreshDTO):
    user_id = decode_refresh_token(dto.refresh_token)
    return TokenDTO(access_token=create_token(user_id),
                    refresh_token=create_refresh_token(user_id))


@router.post("/2fa/request")
def request_2fa(dto: SendCodeDTO, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.phone == dto.phone)
    ).scalars().first()
    if not user or not user.email:
        raise HTTPException(400, "Почта не задана у пользователя")
    resp = AuthService(db).send_code(dto.phone)
    print(f"[EMAIL -> {user.email}] 2FA code: {resp.dev_code}")
    return {"sent": True, "channel": "email", "to": user.email}


@router.post("/2fa/verify", response_model=TokenDTO)
def verify_2fa(dto: LoginDTO, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.phone == dto.phone)
    ).scalars().first()
    if not user:
        raise HTTPException(401, "Пользователь не найден")
    svc = AuthService(db)
    return svc.login(dto)