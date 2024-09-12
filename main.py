from fastapi import Depends, FastAPI, HTTPException, Response, status
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr 
#from configuration.environments import getenv 
from beanie import Document, Indexed, init_beanie
from session import get_mongodb_client 
from schema import schemas 
from database.models import Admin 
from passlib.context import CryptContext

# credentials = getenv()
# username = credentials["username"]
# password =  credentials["password"]
# host =  credentials["host"]
# port =  credentials["port"] 


app = FastAPI() 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str): 
    return pwd_context.hash(password) 
def verify_password(plain_password: str, hashed_password: str): 
    return pwd_context.verify(plain_password, hashed_password)

@app.post("/admin/signup", response_model=schemas.AdminSignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: schemas.AdminSignUp, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)): 
    data = data.model_dump()
    hashed_password = get_hashed_password(data["password"])
    try: 
        insert = Admin(email=data["email"], password=hashed_password)
        await insert.create()
    except Exception as error: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    finally: 
        mongo_client.close()
    return schemas.AdminSignUpResponse(email=insert.email, id=str(insert.id)) 

@app.post("/admin/login", status_code=status.HTTP_200_OK)
async def login(data: schemas.AdminLogin, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)):
    try: 
        data = data.model_dump() 
        results = await Admin.find_one(Admin.email == data["username"])
        if not results: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
        results = results.model_dump()  # since Beanie is also a Pydantic model, we can use the model_dump() method to convert it to a dictionary
        if not verify_password(data["password"], results["password"]): 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials") 
        
        return {"message": "Login successful !!"} 
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) 
    finally:
        mongo_client.close()