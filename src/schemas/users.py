from datetime import datetime
from pydantic import BaseModel, EmailStr, computed_field, model_validator
from typing import Optional
from src.utils.security import get_password_hash


class UserSchema(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    email_confirmed_at: Optional[datetime] = None
    phone_confirmed_at: Optional[datetime] = None

    @computed_field
    @property
    def is_confirmed(self) -> bool:
        return bool(self.email_confirmed_at or self.phone_confirmed_at)

    class Config:
        from_attirbutes = True


class UserSchemaLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

    @model_validator(mode='after')
    def validate_personal_data(self):
        if not self.email and not self.phone:
            raise ValueError('Either email of phone must be provided')
        return self


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


class PhoneConfirmation(BaseModel):
    phone: str
    code: str
