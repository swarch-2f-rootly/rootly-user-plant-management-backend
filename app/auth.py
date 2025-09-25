# app/auth.py 
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

security = HTTPBearer()
SECRET = os.getenv("JWT_SECRET", "changeme")
ALGORITHM = os.getenv("JWT_ALG", "HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="invalid_token")
        return {"user_id": user_id, "roles": payload.get("roles", [])}
    except JWTError:
        raise HTTPException(status_code=401, detail="invalid_token")
