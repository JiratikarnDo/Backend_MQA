import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.Interface.sql_db import getDb
from app.dependencies.auth import get_current_user
from app.endpoint.auth import GoogleLoginRequest
from app.models.courses import Courses
from app.models.users import Users
from app.endpoint.masterdata import fetch_from_rmutto
from schemas.course import CourseCreate, CourseReponseAll, CourseResponse, CourseUpdate

router = APIRouter(prefix="/course", tags=["Course"])


@router.get("/", response_model=List[CourseReponseAll])
async def get_my_department_courses(
    db: Session = Depends(getDb), current_user: Users = Depends(get_current_user)
):

    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )
    courses = (
        db.query(Courses)
        .filter(Courses.department_id == current_user.department_id)
        .all()
    )
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_by_id(
    course_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    course = (
        db.query(Courses)
        .options(joinedload(Courses.category), joinedload(Courses.sub_group))
        .filter(Courses.id == course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ไม่พบรายวิชารหัส ID: {course_id} ในระบบ",
        )

    return course


@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    new_course = Courses(**course_data.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.put("/{course_id}", response_model=CourseUpdate)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    db_course = db.query(Courses).filter(Courses.id == course_id).first()

    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลวิชาที่ต้องการแก้ไข"
        )
    
    update_data = course_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_course, key, value)
    
    try:
        db.commit()
        db.refresh(db_course)
        return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการอัปเดต: {str(e)}")
    
@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    db_course = db.query(Courses).filter(Courses.id == course_id).first()

    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบข้อมูลวิชาที่ต้องการลบ"
        )
    
    try:
        db.delete(db_course)
        db.commit()
        return {"detail": f"ลบรายวิชา ID {course_id} สำเร็จ"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการลบ: {str(e)}")


