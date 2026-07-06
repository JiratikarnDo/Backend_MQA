from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.Interface.sql_db import getDb
from app.models.users import Users
from schemas.user import UserCreate, UserResponse, UserUpdateDepartment, UserUpdateInfo, UserUpdateRole
from app.dependencies.auth import check_admin_staff, get_current_user

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(getDb) , current_user=Depends(get_current_user)):
    if current_user.role not in ["admin", "staff","headmajor"]:
        raise HTTPException(
            status_code=403,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )
    
    try:
        query = db.query(Users).filter(
            Users.role.notin_(["admin", "staff"]),
            Users.id != current_user.id
        )

        users = query.all()
        
        return users
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

@router.get("/users/{user_id}", response_model=UserResponse, summary="Get User Detail", dependencies=[Depends(check_admin_staff)])
async def get_user_detail(user_id: int, db: Session = Depends(getDb)):
    user = db.query(Users).filter(Users.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้ในระบบ")
        
    return user
    
@router.post("/users/", summary="Add New User", dependencies=[Depends(check_admin_staff)])
async def create_user(user_data: UserCreate, db: Session = Depends(getDb)):
    existing_user = db.query(Users).filter(Users.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="อีเมลนี้มีอยู่ในระบบแล้ว")
    
    new_user = Users(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "เพิ่มผู้ใช้ใหม่สำเร็จ", "data": new_user}

@router.patch("/users/{user_id}/info", summary="Edit User Info", dependencies=[Depends(check_admin_staff)])
async def update_user_info(user_id: int, info_data: UserUpdateInfo, db: Session = Depends(getDb)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")
    
    for key, value in info_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
        
    db.commit()
    return {"message": "อัปเดตข้อมูลสำเร็จ"}

@router.patch("/users/{user_id}/department", summary="Change Department", dependencies=[Depends(check_admin_staff)])
async def update_user_department(user_id: int, dept_data: UserUpdateDepartment, db: Session = Depends(getDb)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")
        
    user.department_id = dept_data.department_id
    db.commit()
    return {"message": "เปลี่ยนสาขาสำเร็จ"}

@router.patch("/users/{user_id}/role", summary="Change User Role", dependencies=[Depends(check_admin_staff)])
async def update_user_role(user_id: int, role_data: UserUpdateRole, db: Session = Depends(getDb)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")
        
    user.role = role_data.role
    db.commit()
    return {"message": "เปลี่ยนสิทธิ์การใช้งานสำเร็จ"}