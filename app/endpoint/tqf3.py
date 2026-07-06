from datetime import datetime
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.Interface.sql_db import getDb
from app.dependencies.auth import get_current_user
from app.models.courses import Courses
from app.models.tqf_deadlines import TQFDeadlines
from app.models.users import Users
from schemas.tqf3 import TQF3Create, TQF3Response
from app.models.tqf3 import TQF3Main, TQF3Instructor, TQF3CLO, TQF3Development, TQF3LessonPlan, TQF3Evaluation

router = APIRouter(prefix="/tqf3", tags=["TQF3"])

def build_tqf3_snap_data(course_master):
    credit_total = getattr(course_master, "credit", None) or getattr(course_master, "credits", None) or getattr(course_master, "credit_total", None)
    lecture_hours = getattr(course_master, "lecture_hours", None) or getattr(course_master, "credit_lecture", None) or 0
    practice_hours = getattr(course_master, "practice_hours", None) or getattr(course_master, "credit_lab", None) or 0
    self_study_hours = getattr(course_master, "self_study_hours", None) or getattr(course_master, "credit_self_study", None) or 0

    snap_data = {
        "course_code_snap": getattr(course_master, "course_code", None),
        "course_name_th_snap": getattr(course_master, "course_name_th", None),
        "credits_snap": f"{credit_total} หน่วยกิต ({lecture_hours}-{practice_hours}-{self_study_hours})" if credit_total not in [None, ""] else None
    }

    if hasattr(TQF3Main, "course_name_en_snap"):
        snap_data["course_name_en_snap"] = getattr(course_master, "course_name_en", None)

    return snap_data

def check_tqf_deadline(db: Session, tqf_types: list):
    now = datetime.now()
    
    active_deadline = db.query(TQFDeadlines).filter(
        TQFDeadlines.is_active == True,
        TQFDeadlines.tqf_type.in_(tqf_types)
    ).first()

    if not active_deadline:
        raise HTTPException(
            status_code=400, 
            detail="ขณะนี้ยังไม่มีการเปิดรอบให้จัดทำเอกสารในระบบ"
        )

    if active_deadline.start_date and now < active_deadline.start_date:
        start_str = active_deadline.start_date.strftime("%d/%m/%Y %H:%M")
        raise HTTPException(
            status_code=400, 
            detail=f"ระบบยังไม่เปิดให้ดำเนินการ (จะเปิดระบบในวันที่ {start_str})"
        )

    if active_deadline.end_date and now > active_deadline.end_date:
        end_str = active_deadline.end_date.strftime("%d/%m/%Y %H:%M")
        raise HTTPException(
            status_code=400, 
            detail=f"หมดเขตการดำเนินการแล้ว (ปิดระบบเมื่อ {end_str})"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tqf3(
    data: TQF3Create,
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    user_role = (current_user.role or "").lower()

    if user_role not in ["admin", "staff", "headmajor", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะเจ้าหน้าที่, ผู้ดูแลระบบ, หัวหน้าสาขา หรืออาจารย์เท่านั้นที่ทำรายการนี้ได้",
        )

    course_master = db.query(Courses).filter(Courses.id == data.course_id).first()
    if not course_master:
        raise HTTPException(status_code=404, detail=f"ไม่พบรายวิชารหัส ID: {data.course_id} ในระบบ")

    snap_data = build_tqf3_snap_data(course_master)

    try:
        new_tqf3 = TQF3Main(
            course_id=data.course_id,
            **snap_data,
            curriculum_name=data.curriculum_name,
            course_category=data.course_category,
            semester=data.semester,
            academic_year=data.academic_year,
            year_level=data.year_level,
            section_group=data.section_group,
            student_count=data.student_count,
            location=data.location,
            pre_requisite=data.pre_requisite,
            co_requisite=data.co_requisite,
            updated_at=data.updated_at,
            course_description=data.course_description,
            objectives=data.objectives,
            plo_mapping=data.plo_mapping,
            lecture_hours=data.lecture_hours,
            practice_hours=data.practice_hours,
            self_study_hours=data.self_study_hours,
            contact_detail=data.contact_detail,
            agreements=data.agreements,
            integration_detail=data.integration_detail,
            main_textbooks=data.main_textbooks,
            references=data.references,
            creator_id=current_user.id,
            department_id=current_user.department_id,
            status="draft",
        )

        db.add(new_tqf3)
        db.flush()

        if data.instructors:
            for inst in data.instructors:
                if inst.name:
                    db.add(TQF3Instructor(tqf3_id=new_tqf3.id, name=inst.name))

        if data.clos:
            for clo in data.clos:
                if clo.detail:
                    db.add(TQF3CLO(tqf3_id=new_tqf3.id, number=clo.number, detail=clo.detail))

        if data.development_plans:
            for dev in data.development_plans:
                db.add(TQF3Development(
                    tqf3_id=new_tqf3.id,
                    clo_number=dev.clo_number,
                    teaching_strategy=dev.teaching_strategy,
                    evaluation_strategy=dev.evaluation_strategy
                ))

        if data.lesson_plans:
            for plan in data.lesson_plans:
                db.add(TQF3LessonPlan(
                    tqf3_id=new_tqf3.id,
                    week=plan.week,
                    topic=plan.topic,
                    clos=plan.clos,
                    hours=plan.hours,
                    activities_media=plan.activities_media,
                    instructor_name=plan.instructor_name
                ))

        if data.evaluation_plans:
            for eval_item in data.evaluation_plans:
                db.add(TQF3Evaluation(
                    tqf3_id=new_tqf3.id,
                    activity=eval_item.activity,
                    clo_number=eval_item.clo_number,
                    evaluation_week=eval_item.evaluation_week,
                    proportion_percent=eval_item.proportion_percent
                ))

        db.commit()
        return {"status": "success", "id": new_tqf3.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการบันทึก: {str(e)}")



@router.get("/")
async def get_all_tqf3(
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    query = db.query(TQF3Main)
    user_role = (current_user.role or "").lower()
    
    if user_role in ["staff", "headmajor", "teacher"]:
        query = query.filter(TQF3Main.department_id == current_user.department_id)
    elif user_role in ["admin", "dean"]:
        pass # ดูได้ทั้งหมด
    else:
        return {"status": "success", "data": []}
        
    tqf3_list = query.all()
    return {"status": "success", "total": len(tqf3_list), "data": tqf3_list}



@router.get("/auto-fill/{course_id}")
async def get_tqf3_autofill(
    course_id: int, 
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user)
):
    user_role = (current_user.role or "").lower()
    if user_role not in ["admin", "staff", "headmajor", "teacher"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ไม่มีสิทธิ์ใช้งานส่วนนี้")

    existing_tqf3 = db.query(TQF3Main).options(
        joinedload(TQF3Main.instructors),
        joinedload(TQF3Main.clos),
        joinedload(TQF3Main.lesson_plans),
        joinedload(TQF3Main.evaluation_plans),
        joinedload(TQF3Main.development_plans)
    ).filter(
        TQF3Main.course_id == course_id,
        TQF3Main.creator_id == current_user.id 
    ).first()

    if existing_tqf3:
        return {"is_draft_exist": True, "message": "พบข้อมูลที่ทำไว้ ดึงข้อมูลสำเร็จ", "data": existing_tqf3}
    
    course_master = db.query(Courses).filter(Courses.id == course_id).first()
    if not course_master:
        raise HTTPException(status_code=404, detail="ไม่พบรายวิชานี้ในระบบ")

    auto_fill_data = {
        "course_id": course_master.id,
        "course_code": course_master.course_code,
        "course_name_th": course_master.course_name_th,
        "course_name_en": course_master.course_name_en,
        "credit": course_master.credit,
        "lecture_hours": course_master.lecture_hours,
        "practice_hours": course_master.practice_hours,
        "self_study_hours": course_master.self_study_hours,
        "course_description": course_master.course_description,
        "instructors": [
            {
                "user_id": current_user.id,
                "name": current_user.first_name, # ปรับฟิลด์ให้ตรงกับตาราง Users (เช่น first_name + last_name)
                "role_in_course": "ผู้รับผิดชอบรายวิชา"
            }
        ],
        "clos": [],
        "lesson_plans": [],
        "evaluation_plans": [],
        "development_plans": []
    }

    return {"is_draft_exist": False, "message": "สร้างฟอร์มตั้งต้นเรียบร้อยแล้ว", "data": auto_fill_data}


@router.get("/{tqf3_id}", response_model=TQF3Response)
async def get_tqf3_detail(
    tqf3_id: int,
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    tqf3_data = db.query(TQF3Main).filter(TQF3Main.id == tqf3_id).first()

    if not tqf3_data:
        raise HTTPException(
            status_code=404,
            detail=f"ไม่พบข้อมูล มคอ. 3 รหัส: {tqf3_id}"
        )

    user_role = (current_user.role or "").lower().replace("_", "")

    if user_role in ["admin", "dean"]:
        pass
    elif user_role in ["staff", "headmajor", "teacher"]:
        if tqf3_data.department_id != current_user.department_id:
            raise HTTPException(
                status_code=403,
                detail="คุณไม่มีสิทธิ์เข้าถึงข้อมูล มคอ. 3 ของสาขาอื่น"
            )
    else:
        raise HTTPException(
            status_code=403,
            detail="บทบาทของคุณไม่ได้รับอนุญาตให้ดูข้อมูลนี้"
        )

    instructors = db.query(TQF3Instructor).filter(TQF3Instructor.tqf3_id == tqf3_id).all()
    clos = db.query(TQF3CLO).filter(TQF3CLO.tqf3_id == tqf3_id).all()
    development_plans = db.query(TQF3Development).filter(TQF3Development.tqf3_id == tqf3_id).all()
    lesson_plans = db.query(TQF3LessonPlan).filter(TQF3LessonPlan.tqf3_id == tqf3_id).all()
    evaluation_plans = db.query(TQF3Evaluation).filter(TQF3Evaluation.tqf3_id == tqf3_id).all()

    return {
        "id": tqf3_data.id,
        "course_id": tqf3_data.course_id,

        "course_code_snap": getattr(tqf3_data, "course_code_snap", None),
        "course_name_th_snap": getattr(tqf3_data, "course_name_th_snap", None),
        "course_name_en_snap": getattr(tqf3_data, "course_name_en_snap", None),
        "credits_snap": getattr(tqf3_data, "credits_snap", None),

        "curriculum_name": tqf3_data.curriculum_name,
        "course_category": tqf3_data.course_category,
        "semester": tqf3_data.semester,
        "academic_year": tqf3_data.academic_year,
        "year_level": tqf3_data.year_level,
        "section_group": tqf3_data.section_group,
        "student_count": tqf3_data.student_count,
        "location": tqf3_data.location,
        "pre_requisite": tqf3_data.pre_requisite,
        "co_requisite": tqf3_data.co_requisite,
        "updated_at": tqf3_data.updated_at,
        "course_description": tqf3_data.course_description,
        "objectives": tqf3_data.objectives,
        "plo_mapping": tqf3_data.plo_mapping,
        "lecture_hours": tqf3_data.lecture_hours,
        "practice_hours": tqf3_data.practice_hours,
        "self_study_hours": tqf3_data.self_study_hours,
        "contact_detail": tqf3_data.contact_detail,
        "agreements": tqf3_data.agreements,
        "integration_detail": tqf3_data.integration_detail,
        "main_textbooks": tqf3_data.main_textbooks,
        "references": tqf3_data.references,

        "instructors": [
            {
                "id": item.id,
                "name": item.name
            }
            for item in instructors
        ],
        "clos": [
            {
                "id": item.id,
                "number": item.number,
                "detail": item.detail
            }
            for item in clos
        ],
        "development_plans": [
            {
                "id": item.id,
                "clo_number": item.clo_number,
                "teaching_strategy": item.teaching_strategy,
                "evaluation_strategy": item.evaluation_strategy
            }
            for item in development_plans
        ],
        "lesson_plans": [
            {
                "id": item.id,
                "week": item.week,
                "topic": item.topic,
                "clos": item.clos,
                "hours": item.hours,
                "activities_media": item.activities_media,
                "instructor_name": item.instructor_name
            }
            for item in lesson_plans
        ],
        "evaluation_plans": [
            {
                "id": item.id,
                "activity": item.activity,
                "clo_number": item.clo_number,
                "evaluation_week": item.evaluation_week,
                "proportion_percent": item.proportion_percent
            }
            for item in evaluation_plans
        ]
    }


@router.put("/{tqf3_id}")
async def update_tqf3(
    tqf3_id: int, 
    data: TQF3Create, 
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    existing_tqf3 = db.query(TQF3Main).filter(TQF3Main.id == tqf3_id).first()
    if not existing_tqf3:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล มคอ. 3 ที่ต้องการแก้ไข")

    user_role = (current_user.role or "").lower()

    if user_role in ["admin", "staff", "headmajor", "teacher"]:
        if existing_tqf3.status != "draft":
            raise HTTPException(status_code=400, detail="ไม่สามารถแก้ไขได้ เนื่องจากเอกสารถูกส่งไปให้เจ้าหน้าที่แล้ว") 
        
        if existing_tqf3.department_id != current_user.department_id and user_role != "admin":
            raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์แก้ไขข้อมูล มคอ. 3 ของสาขาอื่น")
            
        if existing_tqf3.creator_id != current_user.id and user_role != "admin":
            raise HTTPException(status_code=403, detail="แก้ไขได้เฉพาะเอกสารที่คุณสร้างเท่านั้น")
    else:
        raise HTTPException(status_code=403, detail="บทบาทของคุณไม่ได้รับอนุญาตให้แก้ไขข้อมูลนี้")
    
    course_master = db.query(Courses).filter(Courses.id == data.course_id).first()
    if not course_master:
        raise HTTPException(status_code=404, detail=f"ไม่พบรายวิชารหัส ID: {data.course_id} ในระบบ")

    snap_data = build_tqf3_snap_data(course_master)

    try:
        existing_tqf3.course_id = data.course_id
        existing_tqf3.course_code_snap = snap_data.get("course_code_snap")
        existing_tqf3.course_name_th_snap = snap_data.get("course_name_th_snap")
        existing_tqf3.credits_snap = snap_data.get("credits_snap")

        if hasattr(existing_tqf3, "course_name_en_snap"):
            existing_tqf3.course_name_en_snap = snap_data.get("course_name_en_snap")

        existing_tqf3.semester = data.semester
        existing_tqf3.academic_year = data.academic_year
        existing_tqf3.year_level = data.year_level
        existing_tqf3.section_group = data.section_group
        existing_tqf3.student_count = data.student_count
        existing_tqf3.location = data.location
        existing_tqf3.pre_requisite = data.pre_requisite
        existing_tqf3.co_requisite = data.co_requisite
        existing_tqf3.course_description = data.course_description
        existing_tqf3.objectives = data.objectives
        existing_tqf3.plo_mapping = data.plo_mapping
        existing_tqf3.lecture_hours = data.lecture_hours
        existing_tqf3.practice_hours = data.practice_hours
        existing_tqf3.self_study_hours = data.self_study_hours
        existing_tqf3.contact_detail = data.contact_detail
        existing_tqf3.agreements = data.agreements
        existing_tqf3.integration_detail = data.integration_detail
        existing_tqf3.main_textbooks = data.main_textbooks
        existing_tqf3.references = data.references
        existing_tqf3.updated_at = data.updated_at

        db.query(TQF3Instructor).filter(TQF3Instructor.tqf3_id == tqf3_id).delete()
        db.query(TQF3CLO).filter(TQF3CLO.tqf3_id == tqf3_id).delete()
        db.query(TQF3Development).filter(TQF3Development.tqf3_id == tqf3_id).delete()
        db.query(TQF3LessonPlan).filter(TQF3LessonPlan.tqf3_id == tqf3_id).delete()
        db.query(TQF3Evaluation).filter(TQF3Evaluation.tqf3_id == tqf3_id).delete()

        if data.instructors:
            for inst in data.instructors:
                if inst.name: db.add(TQF3Instructor(tqf3_id=tqf3_id, name=inst.name))
        
        if data.clos:
            for clo in data.clos:
                db.add(TQF3CLO(tqf3_id=tqf3_id, number=clo.number, detail=clo.detail))
                
        if data.development_plans:
            for dev in data.development_plans:
                db.add(TQF3Development(tqf3_id=tqf3_id, clo_number=dev.clo_number, teaching_strategy=dev.teaching_strategy, evaluation_strategy=dev.evaluation_strategy))
                
        if data.lesson_plans:
            for plan in data.lesson_plans:
                db.add(TQF3LessonPlan(tqf3_id=tqf3_id, week=plan.week, topic=plan.topic, clos=plan.clos, hours=plan.hours, activities_media=plan.activities_media, instructor_name=plan.instructor_name))
                
        if data.evaluation_plans:
            for eval_item in data.evaluation_plans:
                db.add(TQF3Evaluation(tqf3_id=tqf3_id, activity=eval_item.activity, clo_number=eval_item.clo_number, evaluation_week=eval_item.evaluation_week, proportion_percent=eval_item.proportion_percent))

        db.commit()
        return {"status": "success", "message": "อัปเดตข้อมูล มคอ. 3 เรียบร้อยแล้ว"}

    except Exception as e:
        db.rollback()
        if "DataError" in str(e) or "1264" in str(e):
            raise HTTPException(status_code=400, detail="ข้อมูลตัวเลขไม่ถูกต้อง กรุณาตรวจสอบปีการศึกษาหรือจำนวนนักศึกษา")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการอัปเดต: {str(e)}")
    

@router.patch("/{tqf3_id}/submit")
async def submit_tqf3(
    tqf3_id: int, 
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    target_tqf3 = db.query(TQF3Main).filter(TQF3Main.id == tqf3_id).first()
    if not target_tqf3:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล มคอ. 3")

    user_role = (current_user.role or "").lower()
    if user_role not in ["admin", "staff"]:
        if target_tqf3.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="คุณไม่ใช่เจ้าของเอกสารใบนี้")
        
    if user_role not in ["admin", "staff"]:
        check_tqf_deadline(db, ["มคอ.3", "mqa3"])
        
    if target_tqf3.status != "draft":
        raise HTTPException(status_code=400, detail="เอกสารนี้ถูกส่งเข้าระบบไปแล้ว ไม่สามารถส่งซ้ำได้")

    try:
        target_tqf3.status = "pending"  
        db.commit()
        return {
            "status": "success", 
            "message": "ส่งเอกสาร มคอ. 3 เรียบร้อยแล้ว",
            "new_status": target_tqf3.status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")
    

@router.delete("/{tqf3_id}")
async def delete_tqf3(
    tqf3_id: int, 
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    target_tqf3 = db.query(TQF3Main).filter(TQF3Main.id == tqf3_id).first()
    
    if not target_tqf3:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล มคอ. 3 ที่ต้องการลบ")

    user_role = (current_user.role or "").lower()
    
    if user_role in ["admin", "staff"] or target_tqf3.creator_id == current_user.id:
        if target_tqf3.status != "draft":
            raise HTTPException(status_code=400, detail="ไม่สามารถลบได้ เนื่องจากเอกสารถูกส่งเข้าระบบไปแล้ว")
            
        if target_tqf3.department_id != current_user.department_id and user_role != "admin":
            raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์ลบข้อมูล มคอ. 3 ของสาขาอื่น")            
    else:
        raise HTTPException(status_code=403, detail="บทบาทของคุณไม่ได้รับอนุญาตให้ลบข้อมูลนี้")

    try:
        db.delete(target_tqf3)
        db.commit()
        return {"status": "success", "message": f"ลบข้อมูล มคอ. 3 (ID: {tqf3_id}) และรายการย่อยเรียบร้อยแล้ว"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการลบ: {str(e)}")