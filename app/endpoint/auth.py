import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt

# Import ของที่โด้ทำไว้แล้ว
from app.Interface.sql_db import getDb
from app.models.users import User
from app.endpoint.masterdata import fetch_from_rmutto 

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class GoogleLoginRequest(BaseModel):
    token: str

@router.post("/login/google")
async def google_login(request: GoogleLoginRequest, db: Session = Depends(getDb)):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    
    try:
        id_info = id_token.verify_oauth2_token(request.token, requests.Request(), client_id)
        user_email = id_info.get("email")
        
        existing_user = db.query(User).filter(User.email == user_email).first()
        
        if existing_user:
            token = create_access_token({"sub": str(existing_user.id), "email": existing_user.email, "role": existing_user.role})
            return {"message": "เข้าสู่ระบบสำเร็จ", "access_token": token, "role": existing_user.role}
            
        rmutto_res = await fetch_from_rmutto(action="teachers")
        
        if not rmutto_res.get("success"):
            raise HTTPException(status_code=500, detail="ไม่สามารถเชื่อมต่อฐานข้อมูลมหาลัยได้")
            
        teachers_list = rmutto_res.get("data", [])
        
        matched_teacher = None
        for t in teachers_list:
            if t.get("OFFICEREMAIL") == user_email:
                matched_teacher = t
                break

        if not matched_teacher:
            raise HTTPException(status_code=401, detail="อีเมลนี้ไม่มีสิทธิ์เข้าใช้งานระบบ")
            
        full_name = f"{matched_teacher.get('prefix_name', '')}{matched_teacher.get('first_name', '')} {matched_teacher.get('last_name', '')}"
        
        new_user = User(
            email=user_email,
            full_name=full_name,
            role="teacher"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        token = create_access_token({"sub": str(new_user.id), "email": new_user.email, "role": new_user.role})
        return {"message": "ลงทะเบียนและเข้าสู่ระบบสำเร็จ", "access_token": token, "role": new_user.role}

    except ValueError:
        raise HTTPException(status_code=401, detail="Token จาก Google ไม่ถูกต้อง หรือหมดอายุ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))