from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.Interface.sql_db import getDb
from app.dependencies.auth import get_current_user
from app.models.course_openting import (
    CourseOpeningRequest,
    RequestedCourseItem,
    CurriculumResponsiblePerson,
)
from app.models.courses import Courses
from schemas.course_opening import (
    CourseOpeningCreateDraft,
    CourseOpeningDetailResponse,
    CourseOpeningSummaryResponse,
    DeanActionRequest,
)


router = APIRouter(prefix="/course-opening", tags=["Course Opening"])


def getUserRole(current_user):
    return (getattr(current_user, "role", "") or "").lower()


def canReadAll(role: str):
    return role in ["admin", "staff", "dean"]


def canManageRequest(current_user, request_item):
    role = getUserRole(current_user)

    if role in ["admin", "staff"]:
        return True

    if request_item.user_id == current_user.id:
        return True

    if role == "headmajor" and request_item.department_id == current_user.department_id:
        return True

    return False


def getSignatoryName(signatory):
    return signatory.name if signatory else None


def getSignatoryDate(signatory):
    return signatory.signed_date if signatory else None


def buildCreditSnapshot(course):
    credit_total = getattr(course, "credit_total", None)
    credit_lecture = getattr(course, "credit_lecture", None)
    credit_lab = getattr(course, "credit_lab", None)
    credit_self_study = getattr(course, "credit_self_study", None)

    if (
        credit_total is not None
        and credit_lecture is not None
        and credit_lab is not None
        and credit_self_study is not None
    ):
        return f"{credit_total}({credit_lecture}-{credit_lab}-{credit_self_study})"

    return str(credit_total or "")


def validateRequestedCourses(data, db: Session):
    req_course_ids = list(set(item.course_id for item in data.requested_courses))

    if not req_course_ids:
        return {}

    found_courses = db.query(Courses).filter(Courses.id.in_(req_course_ids)).all()

    if len(found_courses) != len(req_course_ids):
        found_ids = [course.id for course in found_courses]
        missing_ids = list(set(req_course_ids) - set(found_ids))
        raise HTTPException(
            status_code=400,
            detail=f"ไม่พบ ID รายวิชา: {missing_ids}",
        )

    return {course.id: course for course in found_courses}


def applyRequestHeaderData(request_item, data):
    request_item.submission_times = data.submission_times
    request_item.semester = data.semester
    request_item.academic_year = data.academic_year
    request_item.curriculum_name = data.curriculum_name
    request_item.major_name = data.major_name
    request_item.program_type = data.program_type
    request_item.study_mode = data.study_mode
    request_item.campus = data.campus
    request_item.target_group = data.target_group
    request_item.is_confirmed = data.is_confirmed

    request_item.head_dept_name = getSignatoryName(data.head_of_department)
    request_item.head_dept_signed = getSignatoryDate(data.head_of_department)

    request_item.vice_dean_name = getSignatoryName(data.vice_dean)
    request_item.vice_dean_signed = getSignatoryDate(data.vice_dean)

    request_item.dean_name = getSignatoryName(data.dean)
    request_item.dean_signed = getSignatoryDate(data.dean)


@router.post("/draft", status_code=status.HTTP_201_CREATED)
@router.post("/Draft", status_code=status.HTTP_201_CREATED)
async def create_draft_request(
    data: CourseOpeningCreateDraft,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    course_master_map = validateRequestedCourses(data, db)

    try:
        new_req = CourseOpeningRequest(
            user_id=current_user.id,
            department_id=current_user.department_id,
            status="draft",
        )

        applyRequestHeaderData(new_req, data)

        db.add(new_req)
        db.flush()

        for item in data.requested_courses:
            master = course_master_map.get(item.course_id)

            db.add(
                RequestedCourseItem(
                    request_id=new_req.id,
                    course_id=master.id,
                    course_code_snapshot=master.course_code,
                    course_name_snapshot=master.course_name_th,
                    credits_snapshot=buildCreditSnapshot(master),
                    year_level=item.year_level,
                    group_no=item.group_no,
                    student_count=item.student_count,
                    is_elective=item.is_elective,
                    is_science_related=item.is_science_related,
                    is_humanities_related=item.is_humanities_related,
                    note=item.note,
                )
            )

        for person in data.responsible_persons:
            db.add(
                CurriculumResponsiblePerson(
                    request_id=new_req.id,
                    name=person.name,
                    signed_date=person.signed_date,
                )
            )

        db.commit()

        return {
            "status": "success",
            "message": "บันทึกแบบร่างสำเร็จ",
            "id": new_req.id,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")


@router.get("/", response_model=list[CourseOpeningSummaryResponse])
async def get_all_opening_requests(
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    role = getUserRole(current_user)
    query = db.query(CourseOpeningRequest)

    if not canReadAll(role):
        query = query.filter(
            CourseOpeningRequest.department_id == current_user.department_id
        )

    offset = (page - 1) * limit

    results = (
        query.order_by(CourseOpeningRequest.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return results


@router.get("/{request_id}", response_model=CourseOpeningDetailResponse)
async def get_opening_request_by_id(
    request_id: int,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    role = getUserRole(current_user)

    result = (
        db.query(CourseOpeningRequest)
        .options(
            joinedload(CourseOpeningRequest.requested_courses),
            joinedload(CourseOpeningRequest.responsible_persons),
        )
        .filter(CourseOpeningRequest.id == request_id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="ไม่พบใบคำร้องที่ระบุ")

    if not canReadAll(role) and result.department_id != current_user.department_id:
        raise HTTPException(
            status_code=403,
            detail="คุณไม่มีสิทธิ์ดูข้อมูลของภาควิชาอื่น",
        )

    return result


@router.put("/{request_id}")
async def update_opening_request(
    request_id: int,
    data: CourseOpeningCreateDraft,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    existing_req = (
        db.query(CourseOpeningRequest)
        .filter(CourseOpeningRequest.id == request_id)
        .first()
    )

    if not existing_req:
        raise HTTPException(status_code=404, detail="ไม่พบใบคำร้องที่ต้องการแก้ไข")

    if not canManageRequest(current_user, existing_req):
        raise HTTPException(
            status_code=403,
            detail="คุณไม่มีสิทธิ์แก้ไขคำร้องนี้",
        )

    if existing_req.status not in ["draft", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail=f"ไม่สามารถแก้ไขเอกสารในสถานะ '{existing_req.status}' ได้",
        )

    course_master_map = validateRequestedCourses(data, db)

    try:
        applyRequestHeaderData(existing_req, data)

        if existing_req.status in ["rejected"]:
            existing_req.status = "draft"
            existing_req.note = None
            existing_req.dean_name = None
            existing_req.dean_signed = None

        db.query(RequestedCourseItem).filter(
            RequestedCourseItem.request_id == request_id
        ).delete(synchronize_session=False)

        db.query(CurriculumResponsiblePerson).filter(
            CurriculumResponsiblePerson.request_id == request_id
        ).delete(synchronize_session=False)

        db.flush()

        for item in data.requested_courses:
            master = course_master_map.get(item.course_id)

            db.add(
                RequestedCourseItem(
                    request_id=existing_req.id,
                    course_id=master.id,
                    course_code_snapshot=master.course_code,
                    course_name_snapshot=master.course_name_th,
                    credits_snapshot=buildCreditSnapshot(master),
                    year_level=item.year_level,
                    group_no=item.group_no,
                    student_count=item.student_count,
                    is_elective=item.is_elective,
                    is_science_related=item.is_science_related,
                    is_humanities_related=item.is_humanities_related,
                    note=item.note,
                )
            )

        for person in data.responsible_persons:
            db.add(
                CurriculumResponsiblePerson(
                    request_id=existing_req.id,
                    name=person.name,
                    signed_date=person.signed_date,
                )
            )

        db.commit()

        return {
            "status": "success",
            "message": "แก้ไขข้อมูลสำเร็จ",
            "new_status": existing_req.status,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update Error: {str(e)}")


@router.delete("/{request_id}")
async def delete_opening_request(
    request_id: int,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    existing_req = (
        db.query(CourseOpeningRequest)
        .filter(CourseOpeningRequest.id == request_id)
        .first()
    )

    if not existing_req:
        raise HTTPException(status_code=404, detail="ไม่พบใบคำร้องที่ต้องการลบ")

    if not canManageRequest(current_user, existing_req):
        raise HTTPException(
            status_code=403,
            detail="คุณไม่มีสิทธิ์ลบคำร้องนี้",
        )

    try:
        db.delete(existing_req)
        db.commit()

        return {
            "status": "success",
            "message": "ลบใบคำร้องเรียบร้อยแล้ว",
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete Error: {str(e)}")


@router.patch("/{request_id}/dean-approval")
async def dean_approve_request(
    request_id: int,
    action: DeanActionRequest,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    role = getUserRole(current_user)

    if role not in ["dean", "admin", "staff"]:
        raise HTTPException(
            status_code=403,
            detail="คุณไม่มีสิทธิ์ดำเนินการในฐานะคณบดี",
        )

    request_item = (
        db.query(CourseOpeningRequest)
        .filter(CourseOpeningRequest.id == request_id)
        .first()
    )

    if not request_item:
        raise HTTPException(status_code=404, detail="ไม่พบใบคำร้องที่ระบุ")

    if request_item.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"ไม่สามารถดำเนินการได้ เนื่องจากเอกสารไม่ได้อยู่ในสถานะรอดำเนินการ "
            f"(สถานะปัจจุบันคือ '{request_item.status}')",
        )

    if action.status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail="สถานะไม่ถูกต้อง ต้องเป็น approved หรือ rejected",
        )

    if action.status == "rejected" and not action.comment:
        raise HTTPException(
            status_code=400,
            detail="กรุณาระบุเหตุผลที่ไม่อนุมัติ",
        )

    try:
        if action.status == "approved":
            request_item.status = "approved"
            request_item.dean_name = f"{current_user.first_name} {current_user.last_name}"
            request_item.dean_signed = date.today()
            message = "อนุมัติใบคำร้องเรียบร้อยแล้ว"

        else:
            request_item.status = "rejected"
            request_item.note = f"คณบดีไม่อนุมัติเนื่องจาก: {action.comment}"
            request_item.dean_name = None
            request_item.dean_signed = None
            message = "ตีกลับใบคำร้องเรียบร้อยแล้ว"

        db.commit()

        return {
            "status": "success",
            "message": message,
            "data": {
                "request_id": request_id,
                "new_status": request_item.status,
                "signed_by": request_item.dean_name,
            },
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"เกิดข้อผิดพลาดในการบันทึก: {str(e)}",
        )


@router.patch("/{request_id}/submit")
async def submit_draft_request(
    request_id: int,
    db: Session = Depends(getDb),
    current_user=Depends(get_current_user),
):
    request_item = (
        db.query(CourseOpeningRequest)
        .filter(CourseOpeningRequest.id == request_id)
        .first()
    )

    if not request_item:
        raise HTTPException(status_code=404, detail="ไม่พบใบคำร้องที่ระบุ")

    if not canManageRequest(current_user, request_item):
        raise HTTPException(
            status_code=403,
            detail="คุณไม่มีสิทธิ์ส่งเอกสารใบนี้",
        )

    if request_item.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="เอกสารนี้ไม่ได้อยู่ในสถานะร่าง ไม่สามารถส่งซ้ำได้",
        )

    required_fields = {
        "ภาคเรียน": request_item.semester,
        "ปีการศึกษา": request_item.academic_year,
        "ชื่อหลักสูตร": request_item.curriculum_name,
        "สาขาวิชา": request_item.major_name,
        "ประเภทหลักสูตร": request_item.program_type,
        "รูปแบบการศึกษา": request_item.study_mode,
        "วิทยาเขต": request_item.campus,
        "กลุ่มเป้าหมาย": request_item.target_group,
    }

    missing_fields = [
        name for name, value in required_fields.items() if not value
    ]

    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"ข้อมูลไม่ครบถ้วน กรุณาระบุ: {', '.join(missing_fields)}",
        )

    requested_courses = (
        db.query(RequestedCourseItem)
        .filter(RequestedCourseItem.request_id == request_id)
        .all()
    )

    if not requested_courses:
        raise HTTPException(
            status_code=400,
            detail="กรุณาเพิ่มข้อมูลรายวิชาที่ต้องการเปิดอย่างน้อย 1 รายการ",
        )

    responsible_persons = (
        db.query(CurriculumResponsiblePerson)
        .filter(CurriculumResponsiblePerson.request_id == request_id)
        .all()
    )

    if not responsible_persons:
        raise HTTPException(
            status_code=400,
            detail="กรุณาเพิ่มข้อมูลผู้รับผิดชอบอย่างน้อย 1 รายการ",
        )

    try:
        request_item.status = "pending"
        db.commit()

        return {
            "status": "success",
            "message": "ส่งใบคำร้องขอเปิดรายวิชาเรียบร้อยแล้ว",
            "new_status": request_item.status,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"เกิดข้อผิดพลาดในการบันทึก: {str(e)}",
        )