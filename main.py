from fastapi import Depends, FastAPI, Request
import asyncio
from pydantic import EmailStr 
from schema import schemas 
from routers import admin, product
from logger import logger 
import time

app = FastAPI() 

@app.middleware("http")
async def log_everything(request: Request, call_next): 
    try: 
        logger.info(f"{request.method} {request.url}\n payload: {request.body()}")
        response = await call_next(request)
        logger.info(f"Response status {response}")
        return response
    except Exception as error:
        logger.error(error, exc_info=True)

app.include_router(admin.router)
app.include_router(product.router)