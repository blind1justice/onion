from sqlalchemy import insert, select
from abc import ABC, abstractmethod

from src.db.session import async_session


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one():
        raise NotImplementedError()
    
    @abstractmethod
    async def find_all():
        raise NotImplementedError()
    

class SQLAclhemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict):
        async with async_session() as session:
            stmt = insert(self.model).values(**data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            inserted_obj = res.scalar_one()
            return inserted_obj.to_read_model()  

    async def find_all(self):
        async with async_session() as session:
            query = select(self.model)
            res = await session.execute(query)
            res = [row[0].to_read_model() for row in res.all()]
            return res
        
    async def find_one(self, id: int):
        async with async_session() as session:
            query = select(self.model).where(self.model.id == id)
            res = await session.execute(query)
            row = res.one_or_none()
            if row:
                return row[0].to_read_model()
            else:
                return None
