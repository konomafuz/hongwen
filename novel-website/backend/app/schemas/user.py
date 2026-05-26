from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)


class UserCreate(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    nickname: str = Field(..., min_length=1, max_length=50)


class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    nickname: str | None = Field(None, min_length=1, max_length=50)