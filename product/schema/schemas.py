from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr 

class AdminSignUp(BaseModel): 
    email: EmailStr 
    password: str 

class AdminSignUpResponse(BaseModel): 
    email: EmailStr 
    id: str 

class AdminLogin(BaseModel): 
    username: EmailStr 
    password: str 

class Token(BaseModel):
    access_token: str
    token_type: str 

class Category(BaseModel):
    name: str
    description: str 

class ProductBase(BaseModel): # schema for product ADD 
    name: str 
    category: Category
    brand: Optional[str] = None
    color: list[str] 
    quantity: int
    price: int

class Product(ProductBase): # schema for product GET
    id: str 
    available: str 

class ProductAddOut(BaseModel): # Response schema for product ADD
    name: str 
    id: str 
    quantity: int 

class ProductFilter(BaseModel): 
    brand: Optional[str] = None
    category: str  
    total_quantity: int 

class ProductUpdate(BaseModel): 
    name: Optional[str] 
    category: Optional[Category]
    brand: Optional[str]
    color: Optional[list[str]] 
    quantity: Optional[int]
    price: Optional[int]