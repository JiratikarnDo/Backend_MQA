from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.Interface.sql_db import getDb
from app.dependencies.auth import check_admin_staff_role
from app.models.tqf_deadlines import TQFDeadlines
from schemas.tqf_deadlines import TQFDeadlineCreate, TQFDeadlineResponse

router = APIRouter(prefix="/tqf", tags=["TQF Deadlines"])


@router.post("/deadlines", response_model=TQFDeadlineResponse)
async def create_tqf_deadline(
    data: TQFDeadlineCreate, 
    db: Session = Depends(getDb),
    current_user = Depends(check_admin_staff_role)
):
    if data.end_date <= data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="วันปิดระบบต้องอยู่หลังวันเปิดระบบเสมอ"
        )
    
    current_year = datetime.now().year + 543 # พ.ศ.
    if data.academic_year < (current_year - 1) or data.academic_year > (current_year + 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ปีการศึกษา {data.academic_year} ไม่ถูกต้อง โปรดตรวจสอบอีกครั้ง"
        )

    existing = db.query(TQFDeadlines).filter(
        TQFDeadlines.tqf_type == data.tqf_type.strip(),
        TQFDeadlines.semester == data.semester,
        TQFDeadlines.academic_year == data.academic_year,
        TQFDeadlines.is_active == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"มีรอบการส่ง {data.tqf_type} ของปี {data.academic_year}/{data.semester} อยู่ในระบบแล้ว"
        )
    
    new_deadline = TQFDeadlines(
        tqf_type=data.tqf_type.strip(),
        semester=data.semester,
        academic_year=data.academic_year,
        start_date=data.start_date,
        end_date=data.end_date,
        is_active=True
    )
    
    db.add(new_deadline)
    try:
        db.commit()
        db.refresh(new_deadline)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดในการบันทึกข้อมูลลงฐานข้อมูล")
        
    return new_deadline


@router.get("/deadlines", response_model=List[TQFDeadlineResponse])
async def get_all_tqf_deadlines(
    db: Session = Depends(getDb),
    current_user = Depends(check_admin_staff_role)
):
    return db.query(TQFDeadlines).order_by(
        TQFDeadlines.academic_year.desc(), 
        TQFDeadlines.semester.desc()
    ).all()


@router.put("/deadlines/{deadline_id}", response_model=TQFDeadlineResponse)
async def update_tqf_deadline(
    deadline_id: int, 
    data: TQFDeadlineCreate,
    db: Session = Depends(getDb),
    current_user = Depends(check_admin_staff_role)
):
    deadline = db.query(TQFDeadlines).filter(TQFDeadlines.id == deadline_id).first()
    if not deadline:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลที่ต้องการแก้ไข")

    if data.end_date <= data.start_date:
        raise HTTPException(status_code=400, detail="วันปิดระบบต้องอยู่หลังวันเปิดระบบเสมอ")

    conflict_check = db.query(TQFDeadlines).filter(
        TQFDeadlines.tqf_type == data.tqf_type.strip(),
        TQFDeadlines.semester == data.semester,
        TQFDeadlines.academic_year == data.academic_year,
        TQFDeadlines.id != deadline_id,
        TQFDeadlines.is_active == True
    ).first()

    if conflict_check:
        raise HTTPException(status_code=409, detail="ข้อมูลที่แก้ไขไปซ้ำกับรอบเวลาอื่นที่มีอยู่แล้ว")

    # อัปเดตข้อมูล
    deadline.tqf_type = data.tqf_type.strip()
    deadline.semester = data.semester
    deadline.academic_year = data.academic_year
    deadline.start_date = data.start_date
    deadline.end_date = data.end_date

    try:
        db.commit()
        db.refresh(deadline)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="ไม่สามารถอัปเดตข้อมูลได้")

    return deadline


@router.delete("/deadlines/{deadline_id}")
async def delete_tqf_deadline(
    deadline_id: int, 
    db: Session = Depends(getDb),
    current_user = Depends(check_admin_staff_role)
):
    deadline = db.query(TQFDeadlines).filter(TQFDeadlines.id == deadline_id).first()
    if not deadline:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลที่ต้องการลบ")

    try:
        db.delete(deadline)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail="ไม่สามารถลบได้ เนื่องจากข้อมูลนี้อาจถูกอ้างอิงในระบบการส่งงานแล้ว"
        )

    return {"message": "ลบข้อมูลสำเร็จ"}