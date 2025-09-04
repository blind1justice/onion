from src.models.posts import Post
from src.utils.repository import SQLAclhemyRepository

from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload
from src.db.session import async_session


class PostRepository(SQLAclhemyRepository):
    model = Post

    async def get_all_with_users(self):
        query = select(self.model).options(joinedload(self.model.user))
        async with async_session() as session:
            res = await session.execute(query)
            res = [row[0].to_read_model() for row in res.all()]
            return res

    async def get_by_id_with_user(self, post_id: int):
        query = select(self.model).where(self.model.id == post_id).options(joinedload(self.model.user))
        async with async_session() as session:
            res = await session.execute(query)
            row = res.one_or_none()
            if row:
                return row[0].to_read_model()
            else:
                return None
            
    async def add_one(self, data: dict):
        async with async_session() as session:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            result = await session.execute(stmt)
            post_id = result.scalar_one() 
            await session.commit()
            res = await self.get_by_id_with_user(post_id)
            return res

