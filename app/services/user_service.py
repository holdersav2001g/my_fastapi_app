import bcrypt
from typing import List, Dict, Any
from bson import ObjectId

class UserService:
    def __init__(self, db):
        self.db = db
        self.user_collection = self.db['users']

    async def add_new_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_data['password'] = hashed_password
        user_data['favourite_groups'] = []
        result = await self.user_collection.insert_one(user_data)
        return await self.user_collection.find_one({'_id': result.inserted_id})

    async def delete_user_by_email(self, email: str):
        await self.user_collection.delete_one({'email': email})

    async def get_all_users(self) -> List[Dict[str, Any]]:
        return await self.user_collection.find({}, {'email': 1, '_id': 0}).to_list(None)

    async def change_password(self, email: str, old_password: str, new_password: str) -> Dict[str, Any]:
        user = await self.user_collection.find_one({'email': email})
        if user and bcrypt.checkpw(old_password.encode('utf-8'), user['password'].encode('utf-8')):
            new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            await self.user_collection.update_one(
                {'email': email},
                {'$set': {'password': new_hashed_password}}
            )
            return {'success': True, 'message': 'Password updated successfully'}
        else:
            return {'success': False, 'message': 'Old password is incorrect'}

    async def save_user_favourite_groups(self, email: str, favourite_groups: List[str]) -> Dict[str, Any]:
        await self.user_collection.update_one(
            {'email': email},
            {'$set': {'favourite_groups': favourite_groups}}
        )
        return {'success': True, 'message': 'Favourite groups updated successfully'}

    async def get_user_by_email(self, email: str) -> Dict[str, Any]:
        return await self.user_collection.find_one({'email': email})