import random
from typing import Optional
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from src.services.sms_service import AbstractSMSService
from src.schemas.users import UserSchema, UserSchemaLogin
from src.config.settings import settings
from src.services.email_service import AbstractEmailService
from src.repositories.users import UserRepository
from src.utils.service import BaseService
from src.utils.security import create_access_token, get_password_hash, verify_password


class UserService(BaseService):
    repo: UserRepository = UserRepository()

    def __init__(self, email_service: AbstractEmailService = None, sms_service: AbstractSMSService = None):
        self.email_service = email_service
        self.sms_service = sms_service

    async def add(self, item):
        if item.email:
            email_exists = await self.repo.find_by_email(item.email)
            if email_exists and not email_exists.email_confirmed_at:
                confirmation_token = str(uuid.uuid4())
                await self.repo.update_email_confirmation_token(item.email, confirmation_token)
                self.email_service.send_confirmation_email(
                    email_exists.email, confirmation_token
                )
                return email_exists
        
        if item.phone:
            phone_exists = await self.repo.find_by_phone(item.phone)
            if phone_exists and not phone_exists.phone_confirmed_at:
                confirmation_code = str(random.randint(100000, 999999))
                await self.repo.update_phone_confirmation_code(item.phone, confirmation_code)
                if self.sms_service:
                    self.sms_service.send_confirmation_sms(
                        item.phone, confirmation_code
                    )
                return phone_exists
        

        item_dict = item.model_dump(exclude={'password'})
        item_dict['hashed_password'] = get_password_hash(item.password)

        if item.email:
            confirmation_token = str(uuid.uuid4())
            item_dict['email_confirmation_token'] = confirmation_token
            item_dict['email_confirmation_sent_at'] = datetime.utcnow()

        if item.phone:
            confirmation_code = str(random.randint(100000, 999999))
            item_dict['phone_confirmation_code'] = confirmation_code
            item_dict['phone_confirmation_sent_at'] = datetime.utcnow()

        item = await self.repo.add_one(item_dict)
        
        if item.email:
            self.email_service.send_confirmation_email(
                item.email, confirmation_token
            )

        if item.phone and self.sms_service:
            self.sms_service.send_confirmation_sms(
                item.phone, confirmation_code
            )

        return item
    
    async def confirm_email(self, token: str) -> bool:
        user = await self.repo.find_by_email_confirmation_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid confirmation token"
            )
        
        if user.email_confirmation_sent_at:
            token_expiry = user.email_confirmation_sent_at + timedelta(hours=24)
            if datetime.utcnow() > token_expiry:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Confirmation token expired"
                )
        
        success = await self.repo.confirm_email(user.id)
            
        return success
    
    async def confirm_phone(self, phone: str, code: str) -> bool:
        user = await self.repo.find_by_phone_confirmation_code(phone, code)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid confirmation code"
            )
        
        if user.phone_confirmation_sent_at:
            code_expiry = user.phone_confirmation_sent_at + timedelta(minutes=10)
            if datetime.utcnow() > code_expiry:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Confirmation code expired"
                )
        
        success = await self.repo.confirm_phone(user.id)
        return success

    async def authenticate_user(self, login_data: UserSchemaLogin) -> Optional[UserSchema]:
        if login_data.email:
            user = await self.repo.find_by_email(login_data.email)
        else:
            user = await self.repo.find_by_phone(login_data.phone)
        
        if not user:
            return None
        
        if not verify_password(login_data.password, user.hashed_password):
            return None
        
        if not user.is_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account not confirmed"
            )
        
        return user
    

    async def create_access_token_for_user(self, user: UserSchema) -> str:
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        return access_token
