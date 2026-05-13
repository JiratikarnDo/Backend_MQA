from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.Interface.sql_db import getDb
from app.models.users import Users
from schemas.user import UserResponse
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(getDb) , current_user=Depends(get_current_user)):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )
    
    try:
        users = db.query(Users).filter(
            Users.role.notin_(["admin", "staff"])
        ).all()
        
        return users
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")