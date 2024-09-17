import jwt 
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError 
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext 


SECRET_KEY = "7f2ed38d5ccf02f1302355c82fdf28a7766ce1d7725a6c63703fc5349dc0f217"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

def get_access_token(data):
    to_encode_payload = data.copy() 
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    to_encode_payload.update({"exp": expire_time}) 
    token = jwt.encode(to_encode_payload, SECRET_KEY, algorithm=ALGORITHM) 
    return token  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str): 
    return pwd_context.hash(password) 
def verify_password(plain_password: str, hashed_password: str): 
    return pwd_context.verify(plain_password, hashed_password) 

def get_user_id(token): 
    '''
    validate the token & return the user_id
    '''
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if not user_id: 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}) 
        return user_id 
    except InvalidTokenError: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})  
    

