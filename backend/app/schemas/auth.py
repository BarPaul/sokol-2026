import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: str
    status: str = "active"
    created_at: dt.datetime | None = None
    last_login_at: dt.datetime | None = None


class AccountCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: str = "editor"


class AccountUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    status: Optional[str] = None


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=4)
    new_password: str = Field(min_length=6, max_length=128)


class PasswordRecoveryRequest(BaseModel):
    email: EmailStr