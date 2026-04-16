import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.Interface.sql_db import getDb
from app.dependencies.auth import get_current_user
from app.endpoint.auth import GoogleLoginRequest
from app.models.courses import Courses
from app.models.users import Users
from app.endpoint.masterdata import fetch_from_rmutto
from schemas.course import CourseCreate, CourseResponse

router = APIRouter(prefix="/course", tags=["Course"])

@router.get("/", response_model=List[CourseResponse])
async def get_my_department_courses(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)):

    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้")
    
    courses = db.query(Courses).filter(Courses.department_id == current_user.department_id).all()
    return courses

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้")
    
    new_course = Courses(
        **course_data.model_dump()
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course