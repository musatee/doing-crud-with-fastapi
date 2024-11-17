from typing import List, Optional
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Response, status, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from prometheus_client import generate_latest
from database.models import Product
from pymongo.errors import DuplicateKeyError, OperationFailure
import oauth
from logger import logger, request_with_payload, request_without_payload # # will inject it as dependency so that every request is logged accordingly
from schema import schemas
from session import get_mongodb_client 
import time, asyncio

router = APIRouter(prefix="/products", tags=["Product"]) 

@router.get("/", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
async def get_products(mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client), limit: int = 10, skip: int = 0, request = Depends(request_without_payload), user_id: str = Depends(oauth.get_user_id)): 
    try:
        await asyncio.sleep(3)
        1/0
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

        try: 
            products = await Product.aggregate(pipeline).to_list()
        except OperationFailure as error: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Operation not permitted")
        if not products: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No products are available")
        
        '''
        I need to return documentID object as a string with named "id" . that's why looped through each dict 
        returned & added "id" key to it and eventually deleting "_id" key 
        ''' 
        for product in products: 
            product["id"] = str(product["_id"])
            del product["_id"]
        logger.info('Request processed successfully (status: 200)')
        return products
    
    except Exception as error: 
        raise error
    finally: 
        mongo_client.close() 

@router.get("/filter", response_model=List[schemas.ProductFilter], status_code=status.HTTP_200_OK)
async def get_products(mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client), category: Optional[str]= None, brand: Optional[str]= None, limit: int = 10, skip: int = 0, request = Depends(request_without_payload), user_id: str = Depends(oauth.get_user_id)): 
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
        try: 
            products = await Product.aggregate(pipeline).to_list()
        except OperationFailure as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation not permitted")
        if not products: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NO products are available")
        logger.info('Request processed successfully (status: 200)')
        return products
    except Exception as error:
        raise error

    finally: 
        mongo_client.close() 

@router.get("/metrics", status_code=status.HTTP_200_OK)
async def expose_metrics(): 
    return Response(content=generate_latest(), media_type="text/plain")

@router.get("/version", status_code=status.HTTP_200_OK)
async def show_version(): 
    await asyncio.sleep(3)
    return {"msg": "app version v1.0-buggy"}

@router.get("/healthz", status_code=status.HTTP_200_OK)
async def check_liveness(mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client)):
    try:
        result = await mongo_client.admin.command("ping")
        if result.get("ok") == 1: 
            return {"status": "UP"}
        else: 
            raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=f"mongodb is unreachable :( )") 
    except Exception as error: 
        raise error


@router.get("/{id}", response_model=List[schemas.Product], status_code=status.HTTP_200_OK)
async def get_products(id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client), request = Depends(request_without_payload), user_id: str = Depends(oauth.get_user_id)): 
    try:
        await asyncio.sleep(3)
        1/0
        ''''
        aggregate is not supported for beanie find_one method. 
        so , returning document using aggregate pipeline directly
        '''
        try: 
            id = PydanticObjectId(id)
        except Exception as error: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"'{id}' is not a valid ID")
        pipeline = [
            {"$match": {"_id": id}},
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
        try:
            products = await Product.aggregate(pipeline).to_list()
        except OperationFailure as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation not permitted")
        if not products: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No products are available")
        
        '''
        I need to return documentID object as a string with named "id" . that's why looped through each dict 
        returned & added "id" key to it and eventually deleting "_id" key 
        '''
        for product in products: 
            product["id"] = str(product["_id"])
            del product["_id"]
        logger.info('Request processed successfully (status: 200)')
        return products
    except Exception as error: 
        raise error
    finally: 
        mongo_client.close() 

@router.post("/", response_model=schemas.ProductAddOut, status_code=status.HTTP_201_CREATED)
async def login(data: schemas.ProductBase, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client), request = Depends(request_with_payload), user_id: str = Depends(oauth.get_user_id)):
    try:
        insert = Product(**data.model_dump())
        await insert.create()
        logger.info('Product added successfully (status: 201)')
        return schemas.ProductAddOut(name=insert.name, id=str(insert.id), quantity=insert.quantity)
    except DuplicateKeyError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Datasets with duplicate name, brand & category are not allowed") 
    finally:
        mongo_client.close() 

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def login(id: str, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client), request = Depends(request_without_payload), user_id: str = Depends(oauth.get_user_id)):
    try:  
        result = await Product.find_one(Product.id == PydanticObjectId(id))
        if not result: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID: {id} not found") 
        await result.delete() 
        logger.info('Product deleted successfully (status: 204)')
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID: {id} not found") 
    finally:
        mongo_client.close() 

@router.put("/{id}", status_code=status.HTTP_201_CREATED)
async def login(id: str, product: schemas.ProductUpdate, mongo_client: AsyncIOMotorClient = Depends(get_mongodb_client), request = Depends(request_with_payload), user_id: str = Depends(oauth.get_user_id)):
    try: 
        result = await Product.find_one(Product.id == PydanticObjectId(id))
        if not result: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID: {id} not found") 
        await result.update({"$set": product.model_dump()})
        updated_data = await Product.get(PydanticObjectId(id)) 
        logger.info('Product updated successfully (status: 201)')
        return {"data": updated_data}

        
    except Exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID: {id} not found")
    finally:
        mongo_client.close() 