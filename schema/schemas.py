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