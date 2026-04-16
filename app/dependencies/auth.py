from datetime import datetime, timedelta, timezone
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer 
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.Interface.sql_db import getDb
from app.models.users import Users


security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(getDb)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="ไม่สามารถยืนยันตัวตนได้ หรือ Token หมดอายุ",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = auth.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError as e:
        raise credentials_exception

    user = db.query(Users).filter(Users.id == int(user_id)).first()
    
    if user is None:
        raise credentials_exception
        
    return user