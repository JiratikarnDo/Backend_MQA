from datetime import date
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.Interface.sql_db import getDb
from app.dependencies.auth import get_current_user
from schemas.tqf5 import TQF5Create, TQF5Response, TQF5_EXAMPLE
from app.models.course_assignment import CourseTeacherAssignment
from app.models.course_openting import CourseOpeningRequest, RequestedCourseItem
from app.models.courses import Courses
from app.models.tqf3 import TQF3Main
from app.models.tqf5 import TQF5Main, TQF5Teacher, TQF5CLOResult, TQF5Grade, TQF5Tolerance, TQF5Issue, TQF5Feedback, TQF5PastPlan, TQF5NextPlan, TQF5ListItem, TQF5Signer

router = APIRouter(prefix="/tqf5", tags=["TQF5"])


def parse_date(value):
    if isinstance(value, date):
        return value

    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    return None


def parse_int(value):
    if value in [None, ""]:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def get_section(document_data: Dict[str, Any], section_name: str) -> Dict[str, Any]:
    section = document_data.get(section_name) or {}
    return section if isinstance(section, dict) else {}


def is_primary_assigned_teacher(course_id: int, teacher_id: int, db: Session):
    return db.query(CourseTeacherAssignment).join(
        RequestedCourseItem,
        CourseTeacherAssignment.requested_course_item_id == RequestedCourseItem.id
    ).join(
        CourseOpeningRequest,
        RequestedCourseItem.request_id == CourseOpeningRequest.id
    ).filter(
        RequestedCourseItem.course_id == course_id,
        CourseTeacherAssignment.teacher_id == teacher_id,
        CourseTeacherAssignment.is_primary.is_(True),
        CourseOpeningRequest.status == "approved",
    ).first()


def check_tqf5_writer_permission(course_id: int, db: Session, current_user):
    user_role = current_user.role.lower()

    if user_role in ["teacher", "headmajor"]:
        if not is_primary_assigned_teacher(course_id, current_user.id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="เฉพาะอาจารย์หลักที่ได้รับมอบหมายรายวิชานี้เท่านั้นที่เขียน มคอ.5 ได้",
            )


def build_teacher_name(teacher):
    return " ".join(
        part for part in [teacher.prefixname, teacher.first_name, teacher.last_name] if part
    )


def build_credit_detail(course: Courses):
    if course.credit_total is None:
        return None

    return f"{course.credit_total}({course.credit_lecture or 0}-{course.credit_lab or 0}-{course.credit_self_study or 0})"


def get_course_clo_rows(course_id: int, db: Session):
    tqf3_data = db.query(TQF3Main).options(
        joinedload(TQF3Main.clos)
    ).filter(TQF3Main.course_id == course_id).order_by(TQF3Main.id.desc()).first()

    if not tqf3_data:
        return []

    return [
        {
            "clo": f"CLO{clo.number}" if clo.number else None,
            "teach": "",
            "assess": "",
            "outcome": clo.detail,
            "improve": "",
        }
        for clo in sorted(tqf3_data.clos, key=lambda item: item.number or 0)
    ]


def update_tqf5_snapshot(tqf5: TQF5Main, document_data: Dict[str, Any]):
    section1 = get_section(document_data, "section1")
    section2 = get_section(document_data, "section2")
    section3 = get_section(document_data, "section3")
    section4 = get_section(document_data, "section4")
    section5 = get_section(document_data, "section5")
    section6 = get_section(document_data, "section6")
    section7 = get_section(document_data, "section7")
    section8 = get_section(document_data, "section8")
    section9 = get_section(document_data, "section9")
    section10 = get_section(document_data, "section10")
    section12 = get_section(document_data, "section12")

    tqf5.courseCode = section1.get("courseCode")
    tqf5.nameThai = section1.get("nameThai")
    tqf5.nameEng = section1.get("nameEng")
    tqf5.credits = parse_int(section2.get("credits"))
    tqf5.creditsDetail = section2.get("creditsDetail")
    tqf5.curriculum = section3.get("curriculum")
    tqf5.courseCategory = section3.get("courseCategory")
    tqf5.teachers = section4.get("teachers")
    tqf5.semester = parse_int(section5.get("semester"))
    tqf5.year = parse_int(section5.get("year"))
    tqf5.yearLevel = parse_int(section5.get("yearLevel"))
    tqf5.groupNumber = parse_int(section5.get("groupNumber") or section5.get("group"))
    tqf5.studentCount = parse_int(section5.get("studentCount"))
    tqf5.location = section6.get("location")
    tqf5.pre = section7.get("pre")
    tqf5.co = section7.get("co")
    tqf5.updatedDate = parse_date(section8.get("updatedDate"))
    tqf5.deviatedHours = section9.get("deviatedHours")
    tqf5.uncoveredTopics = section10.get("uncoveredTopics")
    tqf5.registered = parse_int(section12.get("registered"))
    tqf5.remaining = parse_int(section12.get("remaining"))
    tqf5.withdrawn = parse_int(section12.get("withdrawn"))
    tqf5.abnormalFactor = section12.get("abnormalFactor")


def save_tqf5_details(tqf5_id: int, document_data: Dict[str, Any], db: Session):
    section4 = get_section(document_data, "section4")
    section11 = get_section(document_data, "section11")
    section12 = get_section(document_data, "section12")
    section13 = get_section(document_data, "section13")
    section14 = get_section(document_data, "section14")
    section15 = get_section(document_data, "section15")
    section16 = get_section(document_data, "section16")

    if section4.get("teachers"):
        for teacher_name in section4.get("teachers"):
            if teacher_name:
                db.add(TQF5Teacher(tqf5_id=tqf5_id, name=teacher_name))

    if section11.get("rows"):
        for row in section11.get("rows"):
            db.add(TQF5CLOResult(
                tqf5_id=tqf5_id,
                clo=row.get("clo"),
                teach=row.get("teach"),
                assess=row.get("assess"),
                outcome=row.get("outcome"),
                improve=row.get("improve"),
            ))

    if section12.get("grades"):
        for grade in section12.get("grades"):
            db.add(TQF5Grade(
                tqf5_id=tqf5_id,
                grade=grade.get("grade"),
                range=grade.get("range"),
                count=parse_int(grade.get("count")),
                percent=grade.get("percent"),
            ))

    if section12.get("tolerance"):
        for tolerance in section12.get("tolerance"):
            db.add(TQF5Tolerance(
                tqf5_id=tqf5_id,
                deviation=tolerance.get("deviation"),
                reason=tolerance.get("reason"),
            ))

    if section13.get("resourceIssues"):
        for issue in section13.get("resourceIssues"):
            db.add(TQF5Issue(
                tqf5_id=tqf5_id,
                issue_type="resource",
                issue=issue.get("issue"),
                impact=issue.get("impact"),
            ))

    if section13.get("adminIssues"):
        for issue in section13.get("adminIssues"):
            db.add(TQF5Issue(
                tqf5_id=tqf5_id,
                issue_type="admin",
                issue=issue.get("issue"),
                impact=issue.get("impact"),
            ))

    if section14.get("systemFeedback"):
        for feedback in section14.get("systemFeedback"):
            db.add(TQF5Feedback(
                tqf5_id=tqf5_id,
                feedback_type="system",
                criticism=feedback.get("criticism"),
                response=feedback.get("response"),
            ))

    if section14.get("otherFeedback"):
        for feedback in section14.get("otherFeedback"):
            db.add(TQF5Feedback(
                tqf5_id=tqf5_id,
                feedback_type="other",
                criticism=feedback.get("criticism"),
                response=feedback.get("response"),
            ))

    if section15.get("pastPlans"):
        for plan in section15.get("pastPlans"):
            db.add(TQF5PastPlan(
                tqf5_id=tqf5_id,
                plan=plan.get("plan"),
                result=plan.get("result"),
            ))

    if section15.get("otherActions"):
        for detail in section15.get("otherActions"):
            if detail:
                db.add(TQF5ListItem(tqf5_id=tqf5_id, item_type="other_action", detail=detail))

    if section15.get("recommendations"):
        for detail in section15.get("recommendations"):
            if detail:
                db.add(TQF5ListItem(tqf5_id=tqf5_id, item_type="recommendation", detail=detail))

    if section15.get("nextPlans"):
        for plan in section15.get("nextPlans"):
            db.add(TQF5NextPlan(
                tqf5_id=tqf5_id,
                plan=plan.get("plan"),
                deadline=plan.get("deadline"),
                owner=plan.get("owner"),
            ))

    if section16.get("integrations"):
        for detail in section16.get("integrations"):
            if detail:
                db.add(TQF5ListItem(tqf5_id=tqf5_id, item_type="integration", detail=detail))

    if section16.get("subjectTeachers"):
        for signer in section16.get("subjectTeachers"):
            db.add(TQF5Signer(
                tqf5_id=tqf5_id,
                signer_type="subject",
                name=signer.get("name"),
                signature=signer.get("signature"),
                signed_date=parse_date(signer.get("date")),
            ))

    if section16.get("curriculumTeachers"):
        for signer in section16.get("curriculumTeachers"):
            db.add(TQF5Signer(
                tqf5_id=tqf5_id,
                signer_type="curriculum",
                name=signer.get("name"),
                signature=signer.get("signature"),
                signed_date=parse_date(signer.get("date")),
            ))


def delete_tqf5_details(tqf5_id: int, db: Session):
    db.query(TQF5Teacher).filter(TQF5Teacher.tqf5_id == tqf5_id).delete()
    db.query(TQF5CLOResult).filter(TQF5CLOResult.tqf5_id == tqf5_id).delete()
    db.query(TQF5Grade).filter(TQF5Grade.tqf5_id == tqf5_id).delete()
    db.query(TQF5Tolerance).filter(TQF5Tolerance.tqf5_id == tqf5_id).delete()
    db.query(TQF5Issue).filter(TQF5Issue.tqf5_id == tqf5_id).delete()
    db.query(TQF5Feedback).filter(TQF5Feedback.tqf5_id == tqf5_id).delete()
    db.query(TQF5PastPlan).filter(TQF5PastPlan.tqf5_id == tqf5_id).delete()
    db.query(TQF5NextPlan).filter(TQF5NextPlan.tqf5_id == tqf5_id).delete()
    db.query(TQF5ListItem).filter(TQF5ListItem.tqf5_id == tqf5_id).delete()
    db.query(TQF5Signer).filter(TQF5Signer.tqf5_id == tqf5_id).delete()


@router.get("/autofill/{requested_course_item_id}")
async def get_tqf5_autofill(
    requested_course_item_id: int,
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    item = db.query(RequestedCourseItem).options(
        joinedload(RequestedCourseItem.request),
        joinedload(RequestedCourseItem.teacher_assignments).joinedload(CourseTeacherAssignment.teacher)
    ).filter(RequestedCourseItem.id == requested_course_item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="ไม่พบรายการรายวิชาที่ระบุ")

    if item.request.status != "approved":
        raise HTTPException(status_code=400, detail="ต้องเป็นรายวิชาที่ผ่านการอนุมัติเปิดสอนแล้วเท่านั้น")

    course_master = db.query(Courses).options(
        joinedload(Courses.category),
        joinedload(Courses.sub_group)
    ).filter(Courses.id == item.course_id).first()

    if not course_master:
        raise HTTPException(
            status_code=404,
            detail=f"ไม่พบรายวิชารหัส ID: {item.course_id} ในระบบ กรุณาตรวจสอบอีกครั้ง"
        )

    user_role = current_user.role.lower()

    if user_role not in ["admin", "staff"]:
        if item.request.department_id != current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="คุณไม่มีสิทธิ์ดูข้อมูลรายวิชานอกสาขาของคุณ",
            )

        assigned_teacher_ids = [
            assignment.teacher_id for assignment in item.teacher_assignments
        ]
        if user_role in ["teacher", "headmajor"] and current_user.id not in assigned_teacher_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="คุณไม่มีสิทธิ์ดูข้อมูลรายวิชาที่ไม่ได้รับมอบหมาย",
            )

    sorted_assignments = sorted(item.teacher_assignments, key=lambda assignment: assignment.order_index)
    teacher_names = [
        build_teacher_name(assignment.teacher)
        for assignment in sorted_assignments
        if assignment.teacher
    ]
    primary_assignment = next(
        (assignment for assignment in sorted_assignments if assignment.is_primary),
        None
    )
    primary_teacher_name = (
        build_teacher_name(primary_assignment.teacher)
        if primary_assignment and primary_assignment.teacher
        else None
    )

    course_category = course_master.category.name if course_master.category else None

    return {
        "status": "success",
        "requested_course_item_id": item.id,
        "course_id": course_master.id,
        "primary_teacher": primary_teacher_name,
        "co_teachers": [
            build_teacher_name(assignment.teacher)
            for assignment in sorted_assignments
            if assignment.teacher and not assignment.is_primary
        ],
        "section1": {
            "courseCode": course_master.course_code,
            "nameThai": course_master.course_name_th,
            "nameEng": course_master.course_name_en,
        },
        "section2": {
            "credits": course_master.credit_total,
            "creditsDetail": item.credits_snapshot or build_credit_detail(course_master),
        },
        "section3": {
            "curriculum": [item.request.curriculum_name],
            "courseCategory": course_category,
        },
        "section4": {
            "teachers": teacher_names,
            "primaryTeacher": primary_teacher_name,
        },
        "section5": {
            "semester": item.request.semester,
            "year": item.request.academic_year,
            "yearLevel": item.year_level,
            "group": item.group_no,
            "studentCount": item.student_count,
        },
        "section7": {
            "pre": course_master.prerequisite,
            "co": course_master.corequisite,
        },
        "section11": {
            "rows": get_course_clo_rows(course_master.id, db),
        },
    }


@router.post(
    "/",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": TQF5_EXAMPLE
                }
            }
        }
    }
)
async def create_tqf5(
    data: TQF5Create, 
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):  
    if current_user.role not in ["admin", "staff","headMajor","headmajor","teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="คุณไม่มีสิทธิ์สร้างเอกสาร มคอ.5",
        )

    document_data = data.model_dump(mode="json", exclude_none=True)
    
    course_master = db.query(Courses).filter(Courses.id == data.course_id).first()
    
    if not course_master:
            raise HTTPException(
                status_code=404, 
                detail=f"ไม่พบรายวิชารหัส ID: {data.course_id} ในระบบ กรุณาตรวจสอบอีกครั้ง"
            )

    check_tqf5_writer_permission(data.course_id, db, current_user)
    
    try:
        new_tqf5 = TQF5Main(
            course_id=data.course_id,
            documentData=document_data,
            creator_id=current_user.id,
            department_id=current_user.department_id,
            status="draft",
        )
        update_tqf5_snapshot(new_tqf5, document_data)
        db.add(new_tqf5)
        db.flush()
        save_tqf5_details(new_tqf5.id, document_data, db)
        db.commit()
        return {"status": "success", "id": new_tqf5.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการบันทึก มคอ.5: {str(e)}")
    
@router.get("/")
async def get_all_tqf5(
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    query = db.query(TQF5Main)
    
    if current_user.role.lower() in ["staff", "head"]:
        query = query.filter(TQF5Main.department_id == current_user.department_id)
        
    elif current_user.role.lower() in ["admin", "dean"]:
        pass

    elif current_user.role.lower() in ["headmajor", "teacher"]:
        query = query.filter(TQF5Main.creator_id == current_user.id)
        
    else:
        return {"status": "success", "data": []}

    tqf5_list = query.all()
    
    return {
        "status": "success",
        "total": len(tqf5_list),
        "data": tqf5_list
    }
    
@router.get("/{tqf5_id}", response_model=TQF5Response)
async def get_tqf5_detail(
    tqf5_id: int, 
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    tqf5_data = db.query(TQF5Main).options(
        joinedload(TQF5Main.teachers_list),
        joinedload(TQF5Main.clo_results),
        joinedload(TQF5Main.grades),
        joinedload(TQF5Main.tolerances),
        joinedload(TQF5Main.issues),
        joinedload(TQF5Main.feedbacks),
        joinedload(TQF5Main.past_plans),
        joinedload(TQF5Main.next_plans),
        joinedload(TQF5Main.list_items),
        joinedload(TQF5Main.signers)
    ).filter(TQF5Main.id == tqf5_id).first()
    
    if not tqf5_data:
        raise HTTPException(status_code=404, detail=f"ไม่พบข้อมูล มคอ.5 รหัส: {tqf5_id}")

    user_role = current_user.role.lower()

    if user_role == "admin":
        pass

    elif user_role == "staff":
        if tqf5_data.department_id != current_user.department_id:
            raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์เข้าถึงข้อมูล มคอ.5 ของสาขาอื่น")

    elif user_role in ["headmajor", "teacher"]:
        if tqf5_data.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์เข้าถึงข้อมูล มคอ.5 นี้")
            
    else:
        raise HTTPException(status_code=403, detail="คุณไม่ได้รับอนุญาตให้ดูข้อมูลนี้")

    return tqf5_data
    
@router.put(
    "/{tqf5_id}",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": TQF5_EXAMPLE
                }
            }
        }
    }
)
async def update_tqf5(
    tqf5_id: int, 
    data: TQF5Create, 
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    existing_tqf5 = db.query(TQF5Main).filter(TQF5Main.id == tqf5_id).first()
    if not existing_tqf5:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล มคอ.5 ที่ต้องการแก้ไข")

    user_role = current_user.role.lower()

    if existing_tqf5.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="แก้ไขไม่ได้ เนื่องจากเอกสารถูกส่งแล้ว",
        )
    
    if user_role in ["admin", "staff"]:
        
        if existing_tqf5.department_id != current_user.department_id:
            raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์แก้ไขข้อมูล มคอ.5 ของสาขาอื่น")
            
        if existing_tqf5.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="แก้ไขได้เฉพาะเอกสารที่คุณสร้างเท่านั้น")

    elif user_role in ["headmajor", "teacher"]:
        if existing_tqf5.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="แก้ไขได้เฉพาะเอกสารที่คุณสร้างเท่านั้น")
        
    else:
        raise HTTPException(status_code=403, detail="คุณไม่ได้รับอนุญาตให้แก้ไขข้อมูลนี้")

    document_data = data.model_dump(mode="json", exclude_none=True)
    
    course_master = db.query(Courses).filter(Courses.id == data.course_id).first()
    
    if not course_master:
        raise HTTPException(
            status_code=404, 
            detail=f"ไม่พบรายวิชารหัส ID: {data.course_id} ในระบบ กรุณาตรวจสอบอีกครั้ง"
        )

    check_tqf5_writer_permission(data.course_id, db, current_user)
    
    try:
        existing_tqf5.course_id = data.course_id
        existing_tqf5.documentData = document_data
        update_tqf5_snapshot(existing_tqf5, document_data)
        delete_tqf5_details(tqf5_id, db)
        save_tqf5_details(tqf5_id, document_data, db)

        db.commit()
        return {"status": "success", "message": "อัปเดตข้อมูล มคอ.5 เรียบร้อยแล้ว"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการแก้ไข มคอ.5: {str(e)}")
    
@router.patch("/{tqf5_id}/submit")
async def submit_tqf5(
    tqf5_id: int, 
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    target_tqf5 = db.query(TQF5Main).filter(TQF5Main.id == tqf5_id).first()
    if not target_tqf5:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล มคอ.5")

    if current_user.role.lower() not in ["admin", "staff"]:
        if target_tqf5.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="คุณไม่ใช่เจ้าของเอกสารใบนี้")
        
    if target_tqf5.status != "draft":
        raise HTTPException(status_code=400, detail="เอกสารนี้ถูกส่งเข้าระบบไปแล้ว ไม่สามารถส่งซ้ำได้")

    check_tqf5_writer_permission(target_tqf5.course_id, db, current_user)

    try:
        target_tqf5.status = "pending"  
        db.commit()
        return {
            "status": "success", 
            "message": "ส่งเอกสาร มคอ.5 เรียบร้อยแล้ว",
            "new_status": target_tqf5.status
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")
    
@router.delete("/{tqf5_id}")
async def delete_tqf5(
    tqf5_id: int, 
    db: Session = Depends(getDb),
    current_user = Depends(get_current_user)
):
    target_tqf5 = db.query(TQF5Main).filter(TQF5Main.id == tqf5_id).first()
    
    if not target_tqf5:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล มคอ.5 ที่ต้องการลบ")

    user_role = current_user.role.lower()
    
    if target_tqf5.status != "draft":
            raise HTTPException(
                status_code=400,
                detail="ไม่สามารถลบได้ เนื่องจากเอกสารถูกส่งเข้าระบบไปแล้ว"
        )

    check_tqf5_writer_permission(target_tqf5.course_id, db, current_user)
    
    if user_role in ["admin", "staff"]:
            
        if target_tqf5.department_id != current_user.department_id:
                raise HTTPException(
                    status_code=403,
                    detail="คุณไม่มีสิทธิ์ลบข้อมูล มคอ.5 ของสาขาอื่น"
            )

    elif user_role in ["headmajor", "teacher"]:
        if target_tqf5.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="ลบได้เฉพาะเอกสารที่คุณสร้างเท่านั้น")
                    
    else:
        raise HTTPException(status_code=403, detail="คุณไม่ได้รับอนุญาตให้ลบข้อมูลนี้")

    try:
        db.delete(target_tqf5)
        db.commit()
        return {
            "status": "success", 
            "message": f"ลบข้อมูล มคอ.5 (ID: {tqf5_id}) เรียบร้อยแล้ว"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการลบ: {str(e)}")
