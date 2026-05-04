import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.Interface.sql_db import getDb
from app.dependencies.auth import check_admin_staff_role, get_current_user
from app.endpoint.auth import GoogleLoginRequest
from app.models.courses import Courses
from app.models.users import Users
from app.endpoint.masterdata import fetch_from_rmutto
from schemas.course import CourseCreate, CourseReponseAll, CourseResponse, CourseUpdate

router = APIRouter(prefix="/course", tags=["Course"])


@router.get("/", response_model=List[CourseReponseAll])
async def get_courses(
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
    page: int = Query(1, ge=1, description="เลขหน้า"),
    size: int = Query(10, ge=1, le=100, description="จำนวนข้อมูลต่อหน้า"),
):
    query = db.query(Courses)

    if current_user.role.lower() not in ["admin", "staff"]:
        query = query.filter(Courses.department_id == current_user.department_id)

    offset = (page - 1) * size

    courses = query.order_by(Courses.course_code.asc()).offset(offset).limit(size).all()

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


@router.post("/")
async def create_course(
    data: CourseCreate,
    db: Session = Depends(getDb),
    current_user=Depends(check_admin_staff_role),
):
    existing_course = (
        db.query(Courses).filter(Courses.course_code == data.course_code).first()
    )

    if existing_course:
        raise HTTPException(
            status_code=400,
            detail=f"รหัสวิชา {data.course_code} มีอยู่ในระบบแล้ว ไม่สามารถสร้างซ้ำได้",
        )

    new_course = Courses(**data.dict())
    db.add(new_course)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดในการบันทึกข้อมูล")


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
            detail="ไม่พบข้อมูลวิชาที่ต้องการแก้ไข",
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
        raise HTTPException(
            status_code=500, detail=f"เกิดข้อผิดพลาดในการอัปเดต: {str(e)}"
        )


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
            status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบข้อมูลวิชาที่ต้องการลบ"
        )

    try:
        db.delete(db_course)
        db.commit()
        return {"detail": f"ลบรายวิชา ID {course_id} สำเร็จ"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการลบ: {str(e)}")
