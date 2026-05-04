import os
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
from app.Interface.sql_db import getDb
from app.dependencies.auth import (
    check_admin_staff_role,
    create_access_token,
    get_current_user,
)
from app.models.courses import Courses
from app.models.plo import PLOs, SubPLOs
from app.models.users import Users
from app.endpoint.masterdata import fetch_from_rmutto
from app.models.organization import Departments, Faculties
from schemas.plo import SubPLOCreate
from schemas.user import UserProfileResponse

router = APIRouter(prefix="/plo", tags=["PLOS"])


@router.post("/sub-plos", response_model=dict)
async def create_sub_plo(
    data: SubPLOCreate,
    db: Session = Depends(getDb),
    current_user=Depends(check_admin_staff_role),
):
    parent_plo = db.query(PLOs).filter(PLOs.id == data.plo_id).first()
    if not parent_plo:
        raise HTTPException(
            status_code=404,
            detail=f"ไม่พบ PLO ID {data.plo_id} กรุณาตรวจสอบข้อมูลอีกครั้ง",
        )

    new_sub_plo = SubPLOs(
        sub_plo_code=data.sub_plo_code,
        sub_plo_name_thai=data.sub_plo_name_thai,
        plo_id=data.plo_id,
    )

    db.add(new_sub_plo)
    try:
        db.commit()
        db.refresh(new_sub_plo)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="ไม่สามารถสร้างได้ อาจมีรหัสซ้ำ")

    return {
        "message": "สร้าง Sub-PLO สำเร็จ",
        "id": new_sub_plo.id,
        "code": new_sub_plo.sub_plo_code,
    }


@router.post("/sub-plos/{sub_plo_id}/assign-courses")
async def assign_courses_to_sub_plo(
    sub_plo_id: int,
    course_ids: List[int],
    db: Session = Depends(getDb),
    current_user=Depends(check_admin_staff_role),
):

    unique_course_ids = list(set(course_ids))

    sub_plo = db.query(SubPLOs).filter(SubPLOs.id == sub_plo_id).first()
    if not sub_plo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบ Sub-PLO นี้ในระบบ"
        )

    if not unique_course_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="กรุณาระบุอย่างน้อย 1 รหัสวิชา เพื่อทำการผูกข้อมูล",
        )

    courses = db.query(Courses).filter(Courses.id.in_(unique_course_ids)).all()

    if len(courses) != len(unique_course_ids):
        found_ids = [c.id for c in courses]
        missing_ids = list(set(unique_course_ids) - set(found_ids))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ไม่พบข้อมูลวิชาสำหรับ ID เหล่านี้: {missing_ids}",
        )

    sub_plo.courses = courses

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="เกิดข้อผิดพลาดในการบันทึกข้อมูลลงฐานข้อมูล",
        )

    return {
        "status": "success",
        "message": f"ผูกวิชาจำนวน {len(courses)} วิชา เข้ากับ {sub_plo.sub_plo_code} เรียบร้อยแล้ว",
    }


@router.get("/sub-plos")
async def get_sub_plos_paged(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(getDb),
    current_user=Depends(check_admin_staff_role),
):
    offset = (page - 1) * limit

    total_count = db.query(SubPLOs).count()

    items = (
        db.query(SubPLOs)
        .order_by(SubPLOs.sub_plo_code)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {"total": total_count, "page": page, "limit": limit, "items": items}


@router.get("/sub-plos/{sub_plo_id}")
async def get_sub_plo_by_id(
    sub_plo_id: int,
    db: Session = Depends(getDb),
    current_user=Depends(check_admin_staff_role),
):
    sub_plo = (
        db.query(SubPLOs)
        .options(joinedload(SubPLOs.parent_plo), joinedload(SubPLOs.courses))
        .filter(SubPLOs.id == sub_plo_id)
        .first()
    )

    if not sub_plo:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล Sub-PLO นี้")

    return sub_plo


@router.put("/sub-plos/{sub_plo_id}")
async def update_sub_plo(
    sub_plo_id: int,
    data: SubPLOCreate,
    db: Session = Depends(getDb),
    current_user=Depends(check_admin_staff_role),
):
    sub_plo = db.query(SubPLOs).filter(SubPLOs.id == sub_plo_id).first()
    if not sub_plo:
        raise HTTPException(status_code=404, detail="ไม่พบ Sub-PLO ที่ต้องการแก้ไข")

    if sub_plo.plo_id != data.plo_id:
        parent_exists = db.query(PLOs).filter(PLOs.id == data.plo_id).first()
        if not parent_exists:
            raise HTTPException(status_code=400, detail="PLO ที่ระบุไม่มีอยู่จริง")

    sub_plo.sub_plo_code = data.sub_plo_code
    sub_plo.sub_plo_name_thai = data.sub_plo_name_thai
    sub_plo.plo_id = data.plo_id

    try:
        db.commit()
        db.refresh(sub_plo)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="รหัส Sub-PLO อาจจะซ้ำกับตัวอื่น")

    return {"message": "อัปเดตข้อมูลสำเร็จ", "data": sub_plo}


@router.delete("/sub-plos/{sub_plo_id}")
async def delete_sub_plo(
    sub_plo_id: int,
    db: Session = Depends(getDb),
    current_user=Depends(check_admin_staff_role),
):
    sub_plo = db.query(SubPLOs).filter(SubPLOs.id == sub_plo_id).first()

    if not sub_plo:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลที่ต้องการลบ")

    try:
        db.delete(sub_plo)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="ไม่สามารถลบได้เนื่องจากติดข้อจำกัดของฐานข้อมูล"
        )

    return {
        "message": f"ลบ {sub_plo.sub_plo_code} และความสัมพันธ์ที่เกี่ยวข้องเรียบร้อยแล้ว"
    }


@router.delete("/sub-plos/{sub_plo_id}/courses/{course_id}")
async def unassign_course(
    sub_plo_id: int,
    course_id: int,
    db: Session = Depends(getDb),
    current_user=Depends(check_admin_staff_role),
):
    sub_plo = db.query(SubPLOs).filter(SubPLOs.id == sub_plo_id).first()
    if not sub_plo:
        raise HTTPException(status_code=404, detail="ไม่พบ Sub-PLO")

    course = db.query(Courses).filter(Courses.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="ไม่พบวิชา")

    if course not in sub_plo.courses:
        raise HTTPException(
            status_code=400, detail="วิชานี้ไม่ได้ผูกกับ Sub-PLO นี้อยู่แล้ว"
        )

    sub_plo.courses.remove(course)
    db.commit()

    return {
        "message": f"ยกเลิกการผูกวิชา {course.course_code} ออกจาก {sub_plo.sub_plo_code} เรียบร้อย"
    }
