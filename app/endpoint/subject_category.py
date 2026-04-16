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
from schemas.subject_category import SubjectCategoryResponse, SubjectSubGroupResponse

router = APIRouter(prefix="/subject-category", tags=["Subject Category"])

@router.get("/", response_model=List[SubjectCategoryResponse])
async def get_my_subject_category(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)):
    
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้")
    
    subject_category = db.query(SubjectCategory).all()
    return subject_category

@router.get("/subgroup", response_model=List[SubjectSubGroupResponse])
async def get_subgroups(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)):

    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้")
    

    subgroups = db.query(SubjectSubGroup).all()
    return subgroups

