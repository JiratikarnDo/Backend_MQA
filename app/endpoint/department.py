from http.client import HTTPException

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.Interface.sql_db import getDb
from app.dependencies.auth import get_current_user
from app.models.organization import Departments, Faculties
from app.models.users import Users
from schemas.organization import DepartmentResponseSimple

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("/", response_model=List[DepartmentResponseSimple])
async def get_all_departments(db: Session = Depends(getDb),
                              current_user: Users = Depends(get_current_user)):
    
    if current_user.role not in ["admin", "staff", "headmajor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    results = db.query(
        Departments.id,
        Departments.department_name,
        Departments.faculty_id,
        Faculties.faculty_name
    ).join(Faculties, Departments.faculty_id == Faculties.id).all()
    
    return results