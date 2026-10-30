from typing import Optional
from pydantic import BaseModel


class SendCodeDTO(BaseModel):
    phone: str


class SendCodeResponseDTO(BaseModel):
    sent: bool
    dev_code: Optional[str] = None


class LoginDTO(BaseModel):
    phone: str
    password: Optional[str] = None
    code: Optional[str] = None


class RefreshDTO(BaseModel):
    refresh_token: str


class TokenDTO(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 900