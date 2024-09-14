from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from database.models import Admin 
from pymongo.errors import DuplicateKeyError
from oauth import get_hashed_password, verify_password, get_access_token
from schema import schemas
from session import get_mongodb_client 

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/signup", response_model=schemas.AdminSignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: schemas.AdminSignUp, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)): 
    data = data.model_dump()
    hashed_password = get_hashed_password(data["password"])
    try: 
        insert = Admin(email=data["email"], password=hashed_password)
        await insert.create()
    except DuplicateKeyError: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"{data['email']} is already taken")
    finally: 
        mongo_client.close()
    return schemas.AdminSignUpResponse(email=insert.email, id=str(insert.id)) 

@router.post("/login", response_model=schemas.Token, status_code=status.HTTP_200_OK)
async def login(data: OAuth2PasswordRequestForm = Depends(), mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)):
    try: 
        results = await Admin.find_one(Admin.email == data.username) # since OAuth2PasswordRequestForm object doesn't have model_dump() method
        if not results: 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")
        results = results.model_dump()  # since Beanie is also a Pydantic model, we can use the model_dump() method to convert it to a dictionary
        if not verify_password(data.password, results["password"]): 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials") 
        
        # Call get_access_token function for token & return via respose_model Token to user
        return schemas.Token(access_token=get_access_token({"id": results["id"]}), token_type="bearer")
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) 
    finally:
        mongo_client.close() 
    