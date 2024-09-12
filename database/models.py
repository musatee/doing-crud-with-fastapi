from beanie import Document
from pydantic import EmailStr


class Admin(Document): 
    email: EmailStr 
    password: str

    class Settings: 
        name = "admin"