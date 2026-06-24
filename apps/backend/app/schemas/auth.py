from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.SALES_AGENT


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
