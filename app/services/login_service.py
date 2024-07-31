import bcrypt
from typing import Dict, Any

class LoginService:
    def __init__(self, db):
        self.db = db
        self.user_collection = self.db['users']

    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        user = await self.user_collection.find_one({'email': email})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return {'isAuthenticated': True, 'user': user}
        else:
            return {'isAuthenticated': False, 'error': 'Invalid credentials'}