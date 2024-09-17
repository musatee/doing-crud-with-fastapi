from ast import Set
from typing import List, Optional
from beanie import PydanticObjectId, UpdateResponse
from bson import ObjectId
from fastapi import APIRouter, Depends, Response, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from database.models import Product
from pymongo.errors import DuplicateKeyError
from oauth import get_user_id
from schema import schemas
from session import get_mongodb_client 
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/products", tags=["Product"]) 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
async def get_products(mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client), limit: int = 5, skip: int = 0, user_id = Depends(get_user_id(oauth2_scheme))): 
    try:
        pipeline = [
            {
                "$skip": skip  # Apply skip first
            },
            {
                "$limit": limit  # Then apply limit
            },
            {
                "$project": {
                    "name": 1,
                    "id": 1,
                    "category": 1,
                    "brand": 1,
                    "color": 1,
                    "price": 1,
                    "quantity": 1,
                    "available": {
                        "$cond": {
                            "if": { "$gt": ["$quantity", 0] },  
                            "then": "In-Stock",
                            "else": "Out-Of-Stock"
                        }
                    }
                }
            }
        ]

        products = await Product.aggregate(pipeline).to_list()
        if not products: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No products are available")
        
        '''
        I need to return documentID object as a string with named "id" . that's why looped through each dict 
        returned & added "id" key to it and eventually deleting "_id" key 
        '''
        for product in products: 
            product["id"] = str(product["_id"])
            del product["_id"] 
        print(user_id)
        return products
    except Exception as error: 
        raise error
    finally: 
        mongo_client.close() 

@router.get("/filter", response_model=List[schemas.ProductFilter], status_code=status.HTTP_200_OK)
async def get_products(mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client), category: Optional[str]= None, brand: Optional[str]= None, limit: int = 100, skip: int = 0): 
    try:
        '''
        catch category & brand name as query params if any 
        then add these to $match stage in aggregation pipeline
        '''
        pipeline = [] 
        match = {} 
        if category: 
            match["category.name"] = category 
        if brand: 
            match["brand"] = brand 
        if match: 
            pipeline.append({"$match": match})
        '''
        groups documents into each individual unique category name & brand
        then count/sum number of documents of each individual group
        '''
        group = {
            "$group": {
                "_id": {
                    "category": "$category.name", 
                    "brand": "$brand"
                },
                "total_quantity": { "$sum": "$quantity" }
            }
        }
        pipeline.append(group)

        skip = {
            "$skip": skip
        }
        pipeline.append(skip)

        limit = {
            "$limit": limit
        }
        pipeline.append(limit)

        project = {
            "$project": {
                "brand": "$_id.brand",
                "category": "$_id.category",
                "total_quantity": 1,
                "_id": 0
            }
        }
        pipeline.append(project)

        products = await Product.aggregate(pipeline).to_list()
        if not products: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO products are available")
        return products
    except Exception as error:
        raise error

    finally: 
        mongo_client.close() 

@router.get("/{id}", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
async def get_products(id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)): 
    try:
        ''''
        aggregate is not supported for beanie find_one method. 
        so , returning document using aggregate pipeline directly
        '''
        pipeline = [
            {"$match": {"_id": PydanticObjectId(id)}},
            {
                "$project": {
                    "name": 1,
                    "id": 1,
                    "category": 1,
                    "brand": 1,
                    "color": 1,
                    "price": 1,
                    "quantity": 1,
                    "available": {
                        "$cond": {
                            "if": { "$gt": ["$quantity", 0] },  
                            "then": "In-Stock",
                            "else": "Out-Of-Stock"
                        }
                    }
                }
            }
        ]
        
        products = await Product.aggregate(pipeline).to_list()
        if not products: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No products are available")
        
        '''
        I need to return documentID object as a string with named "id" . that's why looped through each dict 
        returned & added "id" key to it and eventually deleting "_id" key 
        '''
        for product in products: 
            product["id"] = str(product["_id"])
            del product["_id"]
        return products
    except Exception as error: 
        raise error
    finally: 
        mongo_client.close() 

@router.post("/", response_model=schemas.ProductAddOut, status_code=status.HTTP_201_CREATED)
async def login(data: schemas.ProductBase, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)):
    try: 
        insert = Product(**data.model_dump())
        await insert.create()
        return schemas.ProductAddOut(name=insert.name, id=str(insert.id), quantity=insert.quantity)
    except DuplicateKeyError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Datasets with duplicate name, brand & category are not allowed") 
    finally:
        mongo_client.close() 

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def login(id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)):
    try:  
        result = await Product.find_one(Product.id == PydanticObjectId(id))
        if not result: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID: {id} not found") 
        await result.delete() 
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID: {id} not found") 
    finally:
        mongo_client.close() 

@router.put("/{id}", status_code=status.HTTP_201_CREATED)
async def login(id: str, product: schemas.ProductUpdate, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)):
    try: 
        result = await Product.find_one(Product.id == PydanticObjectId(id))
        if not result: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID: {id} not found") 
        await result.update({"$set": product.model_dump()})
        updated_data = await Product.get(PydanticObjectId(id)) 
        return {"data": updated_data}

        
    except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID: {id} not found")
    finally:
        mongo_client.close() 