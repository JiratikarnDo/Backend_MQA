from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.Interface.sql_db import getDb
from app.models.curriculum import Curriculum, CurriculumDepartment
from schemas.curriculum import CurriculumCreate, CurriculumResponse, CurriculumResponseAll, CurriculumUpdate
from app.models.organization import Departments
from app.dependencies.auth import get_current_user
from app.models.users import Users
from sqlalchemy.orm import joinedload


router = APIRouter(prefix="/curriculums", tags=["Curriculums"])

@router.post("/", response_model=CurriculumResponse, status_code=status.HTTP_201_CREATED)
async def create_curriculum(
    curriculum_in: CurriculumCreate,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)
):
    
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )


    if curriculum_in.curriculum_code:
        existing = db.query(Curriculum).filter(Curriculum.curriculum_code == curriculum_in.curriculum_code).first()
        if existing:
            raise HTTPException(status_code=400, detail="รหัสหลักสูตรนี้มีอยู่ในระบบแล้ว")

    if curriculum_in.department_ids:
        existing_depts = db.query(Departments).filter(Departments.id.in_(curriculum_in.department_ids)).all()
        existing_ids = [d.id for d in existing_depts]

        missing_ids = list(set(curriculum_in.department_ids) - set(existing_ids))
        
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ไม่พบสาขา ID: {missing_ids} ในระบบ โปรดตรวจสอบความถูกต้อง"
            )

    try:
        main_data = curriculum_in.model_dump(exclude={"department_ids"})
        new_curriculum = Curriculum(**main_data)
        
        db.add(new_curriculum)
        db.flush()

        if curriculum_in.department_ids:
            existing_shares = db.query(CurriculumDepartment).filter(
                CurriculumDepartment.curriculum_id == new_curriculum.id,
                CurriculumDepartment.department_id.in_(curriculum_in.department_ids)
            ).all()

            if existing_shares:
                existing_dept_ids = [share.department_id for share in existing_shares]
                raise HTTPException(
                    status_code=400,
                    detail=f"มีการแชร์หลักสูตรนี้กับภาควิชา ID: {existing_dept_ids} อยู่แล้ว"
                )
        
        if curriculum_in.department_ids:
            existing_depts = db.query(Departments.id).filter(Departments.id.in_(curriculum_in.department_ids)).all()
            existing_ids = [d.id for d in existing_depts]

            missing_ids = list(set(curriculum_in.department_ids) - set(existing_ids))
            
            if missing_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ไม่พบสาขา ID: {missing_ids} ในระบบ โปรดตรวจสอบความถูกต้อง"
                )
        

        if curriculum_in.department_ids:
            for dept_id in curriculum_in.department_ids:
                new_share = CurriculumDepartment(
                    curriculum_id=new_curriculum.id,
                    department_id=dept_id
                )
                db.add(new_share)

        db.commit()
        db.refresh(new_curriculum)
        
        return new_curriculum

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")
    

@router.get("/", response_model=list[CurriculumResponseAll])
async def get_all_curriculums(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)
):
    
    if current_user.role not in ["admin", "staff", "headmajor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    query = db.query(Curriculum)

    if current_user.role == "headmajor":
            query = query.join(CurriculumDepartment).filter(
                CurriculumDepartment.department_id == current_user.department_id
            )
        
    curriculums = query.all()
    return curriculums


@router.get("/{curriculum_id}", response_model=CurriculumResponse)
async def get_curriculum(
    curriculum_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)
):
    if current_user.role not in ["admin", "staff", "headmajor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    curriculum = db.query(Curriculum).options(
        joinedload(Curriculum.shared_departments)
        .joinedload(CurriculumDepartment.department)
        .joinedload(Departments.faculty)
    ).filter(Curriculum.id == curriculum_id).first()

    if not curriculum:
        raise HTTPException(status_code=404, detail="ไม่พบหลักสูตรนี้ในระบบ")
    
    if current_user.role == "headmajor":
            user_dept_id = current_user.department_id
            allowed_depts = [sd.department_id for sd in curriculum.shared_departments]
            
            if user_dept_id not in allowed_depts:
                raise HTTPException(
                    status_code=403, 
                    detail="คุณไม่มีสิทธิ์ดูหลักสูตรที่ไม่ได้สังกัดสาขาของคุณ"
                )
    
    return curriculum


@router.put("/{curriculum_id}", response_model=CurriculumResponse)
async def update_curriculum(
    curriculum_id: int,
    curriculum_in: CurriculumUpdate,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)
):
    if current_user.role not in ["admin", "staff","headmajor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    db_curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not db_curriculum:
        raise HTTPException(status_code=404, detail="ไม่พบหลักสูตรนี้ในระบบ")

    update_data = curriculum_in.model_dump(exclude_unset=True, exclude={"department_ids"})

    for key, value in update_data.items():
        setattr(db_curriculum, key, value)

    try:
        if curriculum_in.department_ids is not None:
            existing_depts = db.query(Departments.id).filter(Departments.id.in_(curriculum_in.department_ids)).all()
            existing_ids = [d.id for d in existing_depts]
            missing_ids = list(set(curriculum_in.department_ids) - set(existing_ids))
            
            if missing_ids:
                raise HTTPException(status_code=400, detail=f"ไม่พบสาขา ID: {missing_ids}")

            db.query(CurriculumDepartment).filter(CurriculumDepartment.curriculum_id == curriculum_id).delete()
            
            for dept_id in curriculum_in.department_ids:
                new_share = CurriculumDepartment(curriculum_id=curriculum_id, department_id=dept_id)
                db.add(new_share)

        db.commit()
        db.refresh(db_curriculum)
        return db_curriculum

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")
    

@router.patch("/{curriculum_id}/activate", response_model=CurriculumResponse)
async def activate_curriculum(
    curriculum_id: int, 
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)
):
    if current_user.role not in ["admin", "staff","headmajor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="ไม่พบหลักสูตร")


    required_fields = {
        "curriculum_code": "รหัสหลักสูตร",
        "curriculum_name_thai": "ชื่อหลักสูตร (ไทย)",
        "curriculum_level": "ระดับการศึกษา",
        "curriculum_name_english": "ชื่อหลักสูตร (อังกฤษ)"
    }
    
    errors = [msg for field, msg in required_fields.items() if not getattr(curriculum, field)]
    
    if not curriculum.shared_departments:
        errors.append("ต้องระบุสาขาที่ใช้หลักสูตรนี้อย่างน้อย 1 สาขา")

    if errors:
        raise HTTPException(
            status_code=400, 
            detail={"message": "ข้อมูลยังไม่สมบูรณ์", "missing": errors}
        )

    curriculum.status = "success"
    db.commit()
    db.refresh(curriculum)
    
    return curriculum

@router.delete("/{curriculum_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_curriculum(
    curriculum_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)
):
    if current_user.role not in ["admin", "staff","headmajor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้",
        )

    curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="ไม่พบหลักสูตรนี้ในระบบ")

    db.delete(curriculum)
    db.commit()