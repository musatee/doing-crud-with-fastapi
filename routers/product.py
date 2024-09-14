from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from database.models import Product
from pymongo.errors import DuplicateKeyError
from oauth import get_hashed_password, verify_password, get_access_token
from schema import schemas
from session import get_mongodb_client 

router = APIRouter(prefix="/products", tags=["Product"]) 

@router.get("/", response_model=List[schemas.Products], status_code=status.HTTP_200_OK)
async def get_products(mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client), limit: int = 0, skip: int = 0, category: Optional[str] = None): 
    try:
        products = await Product.find().limit(limit).skip(skip).to_list()
        if not products: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No products are available")
        #return schemas.Products(List[products]) 
        return products
    except Exception as error: 
        raise error
    finally: 
        mongo_client.close()