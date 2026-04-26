from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from jose import jwt
from app.Interface.sql_db import getDb
from app.dependencies.auth import get_current_user
from app.models.users import Users
from app.endpoint.masterdata import fetch_from_rmutto
from schemas.course import CourseCreate, CourseResponse
from app.models.subject_category import SubjectCategory, SubjectSubGroup
from schemas.subject_category import (
    SubjectCategoryCreate,
    SubjectCategoryResponse,
    SubjectCategoryUpdate,
    SubjectSubGroupAll,
    SubjectSubGroupCreate,
    SubjectSubGroupResponse,
    SubjectSubGroupUpdate,
)

router = APIRouter(prefix="/subject-category", tags=["Subject Category"])


@router.get("/subgroup", response_model=List[SubjectSubGroupAll])
async def get_subgroups(
    db: Session = Depends(getDb), current_user: Users = Depends(get_current_user)
):

    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    subgroups = db.query(SubjectSubGroup).all()
    return subgroups


@router.post("/", response_model=SubjectCategoryResponse)
async def create_category(
    category_data: SubjectCategoryCreate,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    existing_cat = (
        db.query(SubjectCategory)
        .filter(SubjectCategory.name == category_data.name)
        .first()
    )

    if existing_cat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="มีชื่อหมวดวิชานี้อยู่ในระบบแล้ว",
        )

    new_category = SubjectCategory(**category_data.model_dump())

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}",
        )


@router.post("/subgroup", response_model=SubjectSubGroupResponse)
async def create_subgroup(
    subgroup_data: SubjectSubGroupCreate,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):

    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    parent_category = (
        db.query(SubjectCategory)
        .filter(SubjectCategory.id == subgroup_data.category_id)
        .first()
    )

    if not parent_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบหมวดวิชาหลักที่ระบุ"
        )

    new_subgroup = SubjectSubGroup(**subgroup_data.model_dump())

    try:
        db.add(new_subgroup)
        db.commit()
        db.refresh(new_subgroup)
        return new_subgroup
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}",
        )


@router.get("/", response_model=List[SubjectCategoryResponse])
async def get_my_subject_category(
    db: Session = Depends(getDb), current_user: Users = Depends(get_current_user)
):

    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    subject_category = db.query(SubjectCategory).all()
    return subject_category


@router.put("/{category_id}", response_model=SubjectCategoryResponse)
async def update_category(
    category_id: int,
    data: SubjectCategoryUpdate,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    db_category = (
        db.query(SubjectCategory).filter(SubjectCategory.id == category_id).first()
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="ไม่พบหมวดวิชาที่ระบุ")

    update_data = data.model_dump(exclude_unset=True)

    if "name" in update_data:
        duplicate = (
            db.query(SubjectCategory)
            .filter(
                SubjectCategory.name == update_data["name"],
                SubjectCategory.id != category_id,
            )
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=400, detail="ชื่อหมวดวิชานี้มีอยู่ในระบบแล้ว"
            )

    for key, value in update_data.items():
        setattr(db_category, key, value)

    try:
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{subject_category_id}", response_model=SubjectCategoryResponse)
async def get_subject_category_by_id(
    subject_category_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):

    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    subject_category = (
        db.query(SubjectCategory)
        .filter(SubjectCategory.id == subject_category_id)
        .first()
    )
    if not subject_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบหมวดวิชาที่ระบุ"
        )

    return subject_category


@router.get("/subgroups/{subgroup_id}", response_model=SubjectSubGroupResponse)
async def get_subgroup_by_id(
    subgroup_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):

    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    subgroup = (
        db.query(SubjectSubGroup).filter(SubjectSubGroup.id == subgroup_id).first()
    )
    if not subgroup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบกลุ่มย่อยที่ระบุ"
        )

    return subgroup


@router.put("/subgroups/{subgroup_id}", response_model=SubjectSubGroupResponse)
async def update_subgroup(
    subgroup_id: int,
    data: SubjectSubGroupUpdate,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    db_subgroup = (
        db.query(SubjectSubGroup).filter(SubjectSubGroup.id == subgroup_id).first()
    )
    if not db_subgroup:
        raise HTTPException(status_code=404, detail="ไม่พบกลุ่มย่อยที่ต้องการแก้ไข")

    update_data = data.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category_exists = (
            db.query(SubjectCategory)
            .filter(SubjectCategory.id == update_data["category_id"])
            .first()
        )
        if not category_exists:
            raise HTTPException(status_code=400, detail="ไม่พบหมวดวิชาหลักที่ระบุ")

    for key, value in update_data.items():
        setattr(db_subgroup, key, value)

    try:
        db.commit()
        db.refresh(db_subgroup)
        return db_subgroup
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.delete("/subgroups/{subgroup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subgroup(
    subgroup_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    db_subgroup = (
        db.query(SubjectSubGroup).filter(SubjectSubGroup.id == subgroup_id).first()
    )
    if not db_subgroup:
        raise HTTPException(status_code=404, detail="ไม่พบกลุ่มย่อยที่ต้องการลบ")

    try:
        db.delete(db_subgroup)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    db_category = (
        db.query(SubjectCategory).filter(SubjectCategory.id == category_id).first()
    )
    if not db_category:
        raise HTTPException(status_code=404, detail="ไม่พบหมวดวิชาที่ต้องการลบ")

    try:
        db.delete(db_category)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")
