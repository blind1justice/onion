from abc import ABC

from src.utils.repository import SQLAclhemyRepository


class BaseService():
    repo: SQLAclhemyRepository = None

    async def add(self, item):
        item_dict = item.model_dump()
        item_id = await self.repo.add_one(item_dict)
        return item_id
    
    async def get_all(self):
        res = await self.repo.find_all()
        return res
    
    async def get_one(self, id):
        res = await self.repo.find_one(id)
        return res
