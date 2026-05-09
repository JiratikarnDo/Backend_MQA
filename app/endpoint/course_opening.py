from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from app.Interface.sql_db import getDb
from app.dependencies.auth import get_current_user
from app.models.course_openting import CourseOpeningRequest, RequestedCourseItem, CurriculumResponsiblePerson
from app.models.courses import Courses
from schemas.course_opening import CourseOpeningCreate, CourseOpeningDetailResponse, CourseOpeningSummaryResponse

router = APIRouter(prefix="/course-opening", tags=["Course Opening"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def submit_opening_request(
    data: CourseOpeningCreate, 
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    req_course_ids = list(set(c.course_id for c in data.requested_courses))
    found_courses = db.query(Courses).filter(Courses.id.in_(req_course_ids)).all()

    if len(found_courses) != len(req_course_ids):
        found_ids = [c.id for c in found_courses]
        missing = list(set(req_course_ids) - set(found_ids))
        raise HTTPException(status_code=400, detail=f"ไม่พบ ID รายวิชา: {missing}")

    course_master_map = {c.id: c for c in found_courses}

    try:
        new_req = CourseOpeningRequest(
            submission_times=data.submission_times, semester=data.semester,
            academic_year=data.academic_year, curriculum_name=data.curriculum_name,
            major_name=data.major_name, program_type=data.program_type,
            study_mode=data.study_mode, campus=data.campus, target_group=data.target_group,
            user_id=current_user.id, department_id=current_user.department_id,
            head_dept_name=data.head_of_department.name, head_dept_signed=data.head_of_department.signed_date,
            vice_dean_name=data.vice_dean.name, vice_dean_signed=data.vice_dean.signed_date,
            dean_name=data.dean.name, dean_signed=data.dean.signed_date,
            is_confirmed=data.is_confirmed
        )
        db.add(new_req)
        db.flush()

        for item in data.requested_courses:
            master = course_master_map.get(item.course_id)
            db.add(RequestedCourseItem(
                request_id=new_req.id,
                course_id=master.id,
                course_code_snapshot=master.course_code,
                course_name_snapshot=master.course_name_th,
                credits_snapshot=master.credit_total,
                year_level=item.year_level,
                group_no=item.group_no,
                student_count=item.student_count,
                is_elective=item.is_elective,
                is_science_related=item.is_science_related,
                is_humanities_related=item.is_humanities_related,
                note=item.note
            ))

        for person in data.responsible_persons:
            db.add(CurriculumResponsiblePerson(
                request_id=new_req.id,
                name=person.name,
                signed_date=person.signed_date
            ))

        db.commit()
        return {"status": "success", "id": new_req.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    
@router.get("/", response_model=list[CourseOpeningSummaryResponse])
async def get_all_opening_requests(
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = db.query(CourseOpeningRequest)

    if current_user.role.lower() not in ["admin", "staff","headMajo"]:
        query = query.filter(CourseOpeningRequest.department_id == current_user.department_id)

    offset = (page - 1) * limit
    results = query.order_by(CourseOpeningRequest.created_at.desc()).offset(offset).limit(limit).all()
    
    return results

@router.get("/{request_id}", response_model=CourseOpeningDetailResponse)
async def get_opening_request_by_id(
    request_id: int,
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    result = db.query(CourseOpeningRequest).options(
        joinedload(CourseOpeningRequest.requested_courses),
        joinedload(CourseOpeningRequest.responsible_persons)
    ).filter(CourseOpeningRequest.id == request_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="ไม่พบใบคำร้องที่ระบุ")

    # 🛡️ Security: เช็คสิทธิ์การเข้าถึง
    if current_user.role.lower() not in ["admin", "staff","headMajo"] and \
       result.department_id != current_user.department_id:
        raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์ดูข้อมูลของภาควิชาอื่น")

    return result

@router.put("/{request_id}")
async def update_opening_request(
    request_id: int,
    data: CourseOpeningCreate,
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    existing_req = db.query(CourseOpeningRequest).filter(CourseOpeningRequest.id == request_id).first()
    
    if not existing_req:
        raise HTTPException(status_code=404, detail="ไม่พบใบคำร้องที่ต้องการแก้ไข")
        
    if current_user.role.lower() not in ["admin", "staff", "headMajo"] and \
       existing_req.department_id != current_user.department_id:
        raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์แก้ไขคำร้องของภาควิชาอื่น")

    req_ids = list(set(c.course_id for c in data.requested_courses))
    found_courses = db.query(Courses).filter(Courses.id.in_(req_ids)).all()
    if len(found_courses) != len(req_ids):
        raise HTTPException(status_code=400, detail="พบ ID รายวิชาบางรายการไม่ถูกต้อง")
    course_map = {c.id: c for c in found_courses}

    try:
        update_data = data.model_dump(exclude={"requested_courses", "responsible_persons", "head_of_department", "vice_dean", "dean"})
        for key, value in update_data.items():
            setattr(existing_req, key, value)
        
        existing_req.head_dept_name = data.head_of_department.name
        existing_req.head_dept_signed = data.head_of_department.signed_date
        existing_req.vice_dean_name = data.vice_dean.name
        existing_req.vice_dean_signed = data.vice_dean.signed_date
        existing_req.dean_name = data.dean.name
        existing_req.dean_signed = data.dean.signed_date
        existing_req.requested_courses.clear()
        existing_req.responsible_persons.clear()

        for item in data.requested_courses:
            master = course_map.get(item.course_id)
            credit_str = f"{master.credit_total}({master.credit_lecture}-{master.credit_lab}-{master.credit_self_study})"
            
            new_item = RequestedCourseItem(
                course_id=master.id,
                course_code_snapshot=master.course_code,
                course_name_snapshot=master.course_name_th,
                credits_snapshot=credit_str,
                year_level=item.year_level,
                group_no=item.group_no,
                student_count=item.student_count,
                is_elective=item.is_elective,
                is_science_related=item.is_science_related,
                is_humanities_related=item.is_humanities_related,
                note=item.note
            )
            existing_req.requested_courses.append(new_item)

        for person in data.responsible_persons:
            new_person = CurriculumResponsiblePerson(name=person.name, signed_date=person.signed_date)
            existing_req.responsible_persons.append(new_person)

        db.commit()
        return {"status": "success", "message": "แก้ไขข้อมูลสำเร็จ"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update Error: {str(e)}")


@router.delete("/{request_id}")
async def delete_opening_request(
    request_id: int,
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    existing_req = db.query(CourseOpeningRequest).filter(CourseOpeningRequest.id == request_id).first()
    
    if not existing_req:
        raise HTTPException(status_code=404, detail="ไม่พบใบคำร้องที่ต้องการลบ")
        
    if current_user.role.lower() not in ["admin", "staff","headMajo"] and \
       existing_req.department_id != current_user.department_id:
        raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์ลบคำร้องของภาควิชาอื่น")

    try:
        db.delete(existing_req)
        db.commit()
        return {"status": "success", "message": "ลบใบคำร้องเรียบร้อยแล้ว"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete Error: {str(e)}")