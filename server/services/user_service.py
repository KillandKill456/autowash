from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import hash_password
from ..dto.user_dto import CreateUserDTO, UserDTO
from ..models import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, dto: CreateUserDTO) -> UserDTO:
        existing = self.db.execute(
            select(User).where(User.phone == dto.phone)
        ).scalars().first()
        if existing:
            raise HTTPException(409, "Такой телефон уже зарегистрирован")

        try:
            user = User(
                name=dto.name,
                phone=dto.phone,
                email=dto.email,
                password_hash=hash_password(dto.password),
                role="client",
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except Exception:
            self.db.rollback()
            raise HTTPException(500, "Ошибка регистрации")

        return UserDTO.model_validate(user)

    def get_me(self, user: User) -> UserDTO:
        return UserDTO.model_validate(user)