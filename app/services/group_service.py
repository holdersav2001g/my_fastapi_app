from typing import List, Dict, Any
from bson import ObjectId

class GroupService:
    def __init__(self, db):
        self.db = db
        self.group_collection = self.db['groups']

    async def get_all_groups(self) -> List[Dict[str, Any]]:
        return await self.group_collection.find().to_list(None)

    async def save_group(self, name: str, events: List[str], description: str) -> Dict[str, Any]:
        result = await self.group_collection.update_one(
            {'name': name},
            {'$set': {'events': events, 'description': description}},
            upsert=True
        )
        return await self.group_collection.find_one({'name': name})

    async def delete_group(self, name: str):
        await self.group_collection.delete_one({'name': name})

    async def get_group_details(self, name: str) -> Dict[str, Any]:
        return await self.group_collection.find_one({'name': name})