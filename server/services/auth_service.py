from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import (make_code, check_code, verify_password,
                    create_token, create_refresh_token)
from ..dto.auth_dto import LoginDTO, SendCodeResponseDTO, TokenDTO
from ..models import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def send_code(self, phone: str) -> SendCodeResponseDTO:
        code = make_code(phone)
        return SendCodeResponseDTO(sent=True, dev_code=code)

    def login(self, dto: LoginDTO) -> TokenDTO:
        user = self.db.execute(
            select(User).where(User.phone == dto.phone)
        ).scalars().first()
        if not user:
            raise HTTPException(401, "Неверный телефон или пароль/код")

        ok = False
        if dto.password and verify_password(dto.password, user.password_hash):
            ok = True
        if dto.code and check_code(dto.phone, dto.code):
            ok = True
        if not ok:
            raise HTTPException(401, "Неверный телефон или пароль/код")

        return TokenDTO(access_token=create_token(user.id),
                        refresh_token=create_refresh_token(user.id))