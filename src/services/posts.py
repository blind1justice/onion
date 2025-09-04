import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from src.repositories.posts import PostRepository
from src.config.settings import settings
from src.services.email_service import AbstractEmailService
from src.repositories.users import UserRepository
from src.utils.service import BaseService
from src.utils.security import get_password_hash


class PostService(BaseService):
    repo: PostRepository = PostRepository()

    async def get_all(self):
        posts = await self.repo.get_all_with_users()
        return posts

    async def add(self, item, user_id):
        item_dict = item.model_dump()

        item_dict['user_id'] = user_id

        item = await self.repo.add_one(item_dict)

        return item
