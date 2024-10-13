from typing import Annotated, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from pymongo import IndexModel

class Category(BaseModel):
    name: str
    description: str

class Product(Document): 
    name: str 
    category: Category
    brand: Optional[str] = None
    color: list[str] 
    quantity: int
    price: int 

    '''
    below I've created compund UNIQUE index that ensures no duplicate datasets with same product name, brand & category name is added 
    to database. 
    '''
    class Settings: 
        name = "products"
        indexes = [
            IndexModel(
                [("name", 1),("brand", 1),("category.name", 1)],
                name="test_string_index_DESCENDING",
                unique=True
            )
        ]