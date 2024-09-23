import urllib.parse
from database import models
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

username = "admin"
password = "admin@123"
host = "127.0.0.1"
port = "27017"
encoded_username = urllib.parse.quote_plus(username) 
encoded_password = urllib.parse.quote_plus(password)
connection_string = f"mongodb://{encoded_username}:{encoded_password}@{host}:{port}"

async def get_mongodb_client():
    try:
        client = AsyncIOMotorClient(connection_string) 
        await init_beanie(database=client.ecom, document_models=[models.Admin, models.Product])
        return client
    except Exception as error: 
        raise error