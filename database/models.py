from typing import Annotated, Optional
from beanie import Document, Indexed
from pydantic import EmailStr


class Admin(Document): 
    email: Annotated[EmailStr, Indexed(unique=True)]
    password: str

    class Settings: 
        name = "admin"

class Product(Document): 
    name: str 
    category: str
    brand: Optional[str] = None
    color: str 
    quantity: int

    class Settings: 
        name = "products"