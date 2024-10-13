import jwt, os
from fastapi import Depends, HTTPException, status
from jwt.exceptions import InvalidTokenError 
from fastapi.security.oauth2 import OAuth2PasswordBearer


SECRET_KEY = "7f2ed38d5ccf02f1302355c82fdf28a7766ce1d7725a6c63703fc5349dc0f217"
ALGORITHM = "HS256"
token_url = os.getenv("token_url")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)

def get_user_id(token: str = Depends(oauth2_scheme)): 
    '''
    validate the token & return the user_id
    '''
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if not user_id: 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials, please login", headers={"WWW-Authenticate": "Bearer"}) 
        return user_id 
    except InvalidTokenError: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials, please login", headers={"WWW-Authenticate": "Bearer"})  
    

