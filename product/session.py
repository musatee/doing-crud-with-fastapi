import os
import urllib.parse
from database import models
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

username = os.getenv("db_username")
password = os.getenv("db_password")
host = os.getenv("db_host")
port = os.getenv("db_port", default="27017")

encoded_username = urllib.parse.quote_plus(username) 
encoded_password = urllib.parse.quote_plus(password)
connection_string = f"mongodb://{encoded_username}:{encoded_password}@{host}:{port}"

async def get_mongodb_client():
    try:
        client = AsyncIOMotorClient(connection_string) 
        if client:
            await init_beanie(database=client.ecom, document_models=[models.Product])
            return client 
        else: 
            return None
    except Exception as error:
        raise error 