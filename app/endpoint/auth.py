import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
from app.Interface.sql_db import getDb
from app.dependencies.auth import create_access_token, get_current_user
from app.models.users import Users
from app.endpoint.masterdata import fetch_from_rmutto
from app.models.organization import Departments, Faculties
from schemas.user import UserProfileResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

class GoogleLoginRequest(BaseModel):
    token: str

@router.post("/login/google")
async def google_login(request: GoogleLoginRequest, db: Session = Depends(getDb)):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    
    try:
        id_info = id_token.verify_oauth2_token(request.token, requests.Request(), client_id)
        user_email = id_info.get("email")
        
        existing_user = db.query(Users).filter(Users.email == user_email).first()
        
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
        
        dept_name = matched_teacher.get("DEPARTMENTNAME")
        dept_ref_id = matched_teacher.get("DEPARTMENTID")
        
        dept = db.query(Departments).filter(Departments.external_id == dept_ref_id).first()
        
        if not dept:
            dept = db.query(Departments).filter(Departments.department_name == dept_name).first()

            if not dept:
                dept = Departments(
                    department_name=dept_name,
                    external_id=dept_ref_id
                )
                db.add(dept)
                db.flush()
            else:
                dept.external_id = dept_ref_id
                db.flush()
        
        prefixname = matched_teacher.get('PREFIXNAME')
        first_name = matched_teacher.get('OFFICERNAME')
        last_name = matched_teacher.get('OFFICERSURNAME')

        new_user = Users(
            email=user_email,
            prefixname=prefixname,
            first_name=first_name,
            last_name=last_name,
            department_id=dept.id,
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
    
    
@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: Users = Depends(get_current_user)):
    """
    ดึงข้อมูลเจ้าของ Token เพื่อเอาไปโชว์โปรไฟล์หน้าเว็บ
    """
    return current_user