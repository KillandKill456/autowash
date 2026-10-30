from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..dto.user_dto import CreateUserDTO, UserDTO
from ..models import User
from ..services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserDTO, status_code=201)
def register(dto: CreateUserDTO, db: Session = Depends(get_db)):
    return UserService(db).register(dto)


@router.get("/me", response_model=UserDTO)
def me(user: User = Depends(get_current_user),
       db: Session = Depends(get_db)):
    return UserService(db).get_me(user)