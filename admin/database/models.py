from typing import Annotated
from beanie import Document, Indexed
from pydantic import EmailStr


class Admin(Document): 
    email: Annotated[EmailStr, Indexed(unique=True)]
    password: str

    class Settings: 
        name = "admin"
