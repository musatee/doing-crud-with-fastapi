from fastapi import Depends, FastAPI
import asyncio
from pydantic import EmailStr 
from schema import schemas 
from routers import admin, product

app = FastAPI() 
app.include_router(admin.router)
app.include_router(product.router)