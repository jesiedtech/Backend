from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import datetime
import re
from uuid import UUID

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    is_verified: bool
    is_active: bool

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str
        }

class UserVerify(BaseModel):
    token: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

    @validator('new_password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class Token(BaseModel):
    access_token: str
    token_type: str

class User(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str
        }

class RoleAssignment(BaseModel):
    user_id: UUID
    role: str 