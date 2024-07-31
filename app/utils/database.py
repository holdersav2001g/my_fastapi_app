from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from app.config import settings
from urllib.parse import urlparse

# Parse the MongoDB URL to get the database name
parsed_url = urlparse(settings.MONGODB_URL)
db_name = parsed_url.path.lstrip('/') or 'your_database_name'  # Fallback to 'your_database_name' if not specified

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[db_name]

def get_db():
    return db

async def connect_to_mongo():
    try:
        await client.admin.command('ping')
        print(f"Connected to MongoDB database: {db_name}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    client.close()
    print("Closed MongoDB connection")