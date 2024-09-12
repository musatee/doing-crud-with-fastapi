from fastapi import Depends, FastAPI 
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr 
#from configuration.environments import getenv 
from beanie import Document, Indexed, init_beanie
from session import get_mongodb_client 
from schema import schemas 
from database.models import Admin

# credentials = getenv()
# username = credentials["username"]
# password =  credentials["password"]
# host =  credentials["host"]
# port =  credentials["port"] 


app = FastAPI() 

@app.post("/admin/signup", response_model=schemas.AdminSignUpResponse)
async def welcome(data: schemas.AdminSignUp, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)): 
    data = data.model_dump()
    try: 
        insert = Admin(email=data["email"], password=data["password"])
        await insert.create()
    except Exception as error: 
        print("went wrong")
    finally: 
        mongo_client.close()
    return schemas.AdminSignUpResponse(email=insert.email, id=str(insert.id))