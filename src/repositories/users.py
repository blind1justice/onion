from datetime import datetime, timezone

from pydantic import EmailStr
from src.models.users import User
from src.utils.repository import SQLAclhemyRepository

from sqlalchemy import insert, select, update
from src.db.session import async_session

class UserRepository(SQLAclhemyRepository):
    model = User

    async def find_by_phone_confirmation_code(self, phone: str, code: str):
        async with async_session() as session:
            query = select(self.model).where(
                self.model.phone == phone,
                self.model.phone_confirmation_code == code
            )
            res = await session.execute(query)
            return res.scalar_one_or_none()
        
    async def find_by_phone(self, phone: str):
        async with async_session() as session:
            query = select(self.model).where(self.model.phone == phone)
            res = await session.execute(query)
            return res.scalar_one_or_none()

    async def find_by_email(self, email: EmailStr):
        async with async_session() as session:
            query = select(self.model).where(self.model.email == email)
            res = await session.execute(query)
            return res.scalar_one_or_none()

    async def find_by_email_confirmation_token(self, token: str):
        async with async_session() as session:
            query = select(self.model).where(self.model.email_confirmation_token == token)
            res = await session.execute(query)
            return res.scalar_one_or_none()

    async def confirm_email(self, user_id: int) -> bool:
        async with async_session() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == user_id)
                .values(
                    email_confirmed_at=datetime.utcnow(),
                    email_confirmation_token=None
                )
            )
            await session.execute(stmt)
            await session.commit()
            return True

    async def update_email_confirmation_token(self, email: EmailStr, token: str):
        async with async_session() as session:
            stmt = (
                update(self.model)
                .where(self.model.email == email)
                .values(
                    email_confirmation_token=token,
                    email_confirmation_sent_at=datetime.utcnow()
                )
            )
            await session.execute(stmt)
            await session.commit()
    
    async def confirm_phone(self, user_id: int) -> bool:
        async with async_session() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == user_id)
                .values(
                    phone_confirmed_at=datetime.utcnow(),
                    phone_confirmation_code=None
                )
            )
            await session.execute(stmt)
            await session.commit()
            return True
        
    async def update_phone_confirmation_code(self, phone: str, code: str):
        async with async_session() as session:
            stmt = (
                update(self.model)
                .where(self.model.phone == phone)
                .values(
                    phone_confirmation_code=code,
                    phone_confirmation_sent_at=datetime.utcnow()
                )
            )
            await session.execute(stmt)
            await session.commit()

