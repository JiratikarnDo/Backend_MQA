from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from app.Interface.sql_db import getDb
from app.dependencies.auth import check_admin_staff_role, get_current_user
from app.endpoint.auth import GoogleLoginRequest
from app.models.courses import Courses
from app.models.organization import Departments
from app.models.subject_category import SubjectCategory, SubjectSubGroup
from app.models.users import Users
from app.endpoint.masterdata import fetch_from_rmutto
from schemas.course import CourseCreate, CourseReponseAll, CourseResponse, CourseUpdate

router = APIRouter(prefix="/course", tags=["Course"])


class SubjectDocxPayload(BaseModel):
    courseCode: str
    curriculumLevel: Optional[str] = "bachelor"
    courseNameThai: Optional[str] = ""
    courseNameEnglish: Optional[str] = ""
    subjectCategory: Optional[str] = "specific"
    subCategory: Optional[str] = "หมวดวิชาเฉพาะ"
    studyLine: Optional[str] = "สายวิทยาศาสตร์"
    totalCredits: Optional[int] = 0
    lectureHours: Optional[int] = 0
    labHours: Optional[int] = 0
    selfStudyHours: Optional[int] = 0
    descriptionThai: Optional[str] = ""
    descriptionEnglish: Optional[str] = ""
    hasPreSubjects: Optional[str] = "no"
    preSubjects: Optional[List[str]] = []
    hasCoSubjects: Optional[str] = "no"
    coSubjects: Optional[List[str]] = []
    departmentId: Optional[int] = None


categoryNameMap = {
    "generalEducation": "หมวดวิชาศึกษาทั่วไป",
    "specific": "หมวดวิชาเฉพาะ",
    "freeElective": "หมวดวิชาเลือกเสรี",
}


def normalizeSubjectCategory(subjectCategory: Optional[str]) -> str:
    if subjectCategory in categoryNameMap:
        return subjectCategory

    text = str(subjectCategory or "").strip()

    if "ศึกษา" in text or "ทั่วไป" in text:
        return "generalEducation"

    if "เลือกเสรี" in text or text == "free":
        return "freeElective"

    return "specific"


def getDepartmentDisplayName(department: Optional[Departments]) -> str:
    if not department:
        return ""

    return (
        getattr(department, "department_name", None)
        or getattr(department, "major_name", None)
        or getattr(department, "name", None)
        or ""
    )


def buildDepartmentNameMap(db: Session, departmentIds: List[int]) -> dict:
    cleanDepartmentIds = sorted({int(departmentId) for departmentId in departmentIds if departmentId})

    if not cleanDepartmentIds:
        return {}

    departments = db.query(Departments).filter(Departments.id.in_(cleanDepartmentIds)).all()
    return {department.id: getDepartmentDisplayName(department) for department in departments}


def resolveDepartmentId(db: Session, departmentId: Optional[int], currentUser: Users) -> int:
    candidateIds = []

    if departmentId:
        candidateIds.append(departmentId)

    if getattr(currentUser, "department_id", None):
        candidateIds.append(currentUser.department_id)

    for candidateId in candidateIds:
        department = db.query(Departments).filter(Departments.id == candidateId).first()

        if department:
            return department.id

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ไม่พบรหัสสาขา/ภาควิชาในระบบ กรุณาเลือกสาขาที่มีอยู่จริง หรือให้ผู้ใช้มี department_id")


def getOrCreateCategory(db: Session, subjectCategory: Optional[str]) -> SubjectCategory:
    categoryKey = normalizeSubjectCategory(subjectCategory)
    categoryName = categoryNameMap.get(categoryKey, "หมวดวิชาเฉพาะ")
    category = db.query(SubjectCategory).filter(SubjectCategory.name == categoryName).first()

    if category:
        return category

    category = SubjectCategory(name=categoryName)
    db.add(category)
    db.flush()
    return category


def getOrCreateSubGroup(db: Session, category: SubjectCategory, subCategory: Optional[str]) -> Optional[SubjectSubGroup]:
    subGroupName = str(subCategory or "").strip()

    if not subGroupName:
        return None

    subGroup = db.query(SubjectSubGroup).filter(SubjectSubGroup.name == subGroupName, SubjectSubGroup.category_id == category.id).first()

    if subGroup:
        return subGroup

    subGroup = SubjectSubGroup(name=subGroupName, category_id=category.id)
    db.add(subGroup)
    db.flush()
    return subGroup


def joinSubjectList(values: Optional[List[str]]) -> str:
    if not values:
        return ""

    return ", ".join([str(value).strip() for value in values if str(value).strip()])


def subjectPayloadToResponse(course: Courses, sourcePayload: Optional[dict] = None) -> dict:
    sourcePayload = sourcePayload or {}
    categoryName = course.category.name if course.category else ""
    subGroupName = course.sub_group.name if course.sub_group else ""
    departmentName = (
        sourcePayload.get("departmentName")
        or sourcePayload.get("department_name")
        or sourcePayload.get("majorName")
        or sourcePayload.get("major_name")
        or getDepartmentDisplayName(getattr(course, "department", None))
        or ""
    )

    if "ศึกษาทั่วไป" in categoryName:
        subjectCategory = "generalEducation"
    elif "เลือกเสรี" in categoryName:
        subjectCategory = "freeElective"
    else:
        subjectCategory = "specific"

    return {
        "id": course.id,
        "courseCode": course.course_code or "",
        "course_code": course.course_code or "",
        "curriculumLevel": course.course_level or sourcePayload.get("curriculumLevel") or "bachelor",
        "course_level": course.course_level or sourcePayload.get("curriculumLevel") or "bachelor",
        "courseNameThai": course.course_name_th or "",
        "course_name_th": course.course_name_th or "",
        "courseNameEnglish": course.course_name_en or "",
        "course_name_en": course.course_name_en or "",
        "departmentId": course.department_id,
        "department_id": course.department_id,
        "departmentName": departmentName,
        "department_name": departmentName,
        "majorName": departmentName,
        "major_name": departmentName,
        "department": {"id": course.department_id, "department_name": departmentName, "departmentName": departmentName, "name": departmentName} if departmentName else None,
        "subjectCategory": sourcePayload.get("subjectCategory") or subjectCategory,
        "subCategory": subGroupName or sourcePayload.get("subCategory") or "",
        "studyLine": course.subject_line or sourcePayload.get("studyLine") or "สายวิทยาศาสตร์",
        "totalCredits": course.credit_total or 0,
        "lectureHours": course.credit_lecture or 0,
        "labHours": course.credit_lab or 0,
        "selfStudyHours": course.credit_self_study or 0,
        "credit_total": course.credit_total or 0,
        "credit_lecture": course.credit_lecture or 0,
        "credit_lab": course.credit_lab or 0,
        "credit_self_study": course.credit_self_study or 0,
        "descriptionThai": course.description_thai or "",
        "descriptionEnglish": course.description_english or "",
        "description_thai": course.description_thai or "",
        "description_english": course.description_english or "",
        "hasPreSubjects": "yes" if course.prerequisite else "no",
        "preSubjects": [course.prerequisite] if course.prerequisite else [],
        "hasCoSubjects": "yes" if course.corequisite else "no",
        "coSubjects": [course.corequisite] if course.corequisite else [],
        "prerequisite": course.prerequisite or "",
        "corequisite": course.corequisite or "",
        "category_id": course.category_id,
        "sub_group_id": course.sub_group_id,
        "subject_line": course.subject_line or "",
        "created_at": course.created_at if hasattr(course, "created_at") else None,
        "update_at": course.update_at if hasattr(course, "update_at") else None,
    }


def saveSubjectPayload(db: Session, payload: SubjectDocxPayload, currentUser: Users) -> tuple[Courses, bool]:
    departmentId = resolveDepartmentId(db, payload.departmentId, currentUser)
    category = getOrCreateCategory(db, payload.subjectCategory)
    subGroup = getOrCreateSubGroup(db, category, payload.subCategory)
    courseCode = str(payload.courseCode or "").strip()

    if not courseCode:
        raise HTTPException(status_code=400, detail="ไม่พบรหัสวิชา")

    course = db.query(Courses).filter(Courses.course_code == courseCode, Courses.department_id == departmentId).first()
    isCreated = course is None

    if course is None:
        course = Courses(course_code=courseCode, department_id=departmentId)
        db.add(course)

    course.course_level = payload.curriculumLevel or "bachelor"
    course.course_name_th = payload.courseNameThai or ""
    course.course_name_en = payload.courseNameEnglish or ""
    course.category_id = category.id
    course.sub_group_id = subGroup.id if subGroup else None
    course.subject_line = payload.studyLine or "สายวิทยาศาสตร์"
    course.credit_total = int(payload.totalCredits or 0)
    course.credit_lecture = int(payload.lectureHours or 0)
    course.credit_lab = int(payload.labHours or 0)
    course.credit_self_study = int(payload.selfStudyHours or 0)
    course.description_thai = payload.descriptionThai or ""
    course.description_english = payload.descriptionEnglish or ""
    course.prerequisite = joinSubjectList(payload.preSubjects)
    course.corequisite = joinSubjectList(payload.coSubjects)
    course.department_id = departmentId

    db.flush()
    db.refresh(course)

    return course, isCreated


@router.post("/add-subject")
async def add_subject_from_form(payload: SubjectDocxPayload, db: Session = Depends(getDb), current_user: Users = Depends(check_admin_staff_role)):
    try:
        course, isCreated = saveSubjectPayload(db, payload, current_user)
        db.commit()
        db.refresh(course)

        return {
            "message": "เพิ่มรายวิชาสำเร็จ" if isCreated else "อัปเดตรายวิชาสำเร็จ",
            "created": isCreated,
            "subject": subjectPayloadToResponse(course, payload.model_dump()),
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการบันทึกรายวิชา: {str(e)}")


@router.get("/")
async def get_courses(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
    page: int = Query(1, ge=1, description="เลขหน้า"),
    size: int = Query(1000, ge=1, le=2000, description="จำนวนข้อมูลต่อหน้า"),
    departmentId: Optional[int] = Query(None, description="รหัสสาขา/ภาควิชาที่ต้องการดึงรายวิชา"),
):
    query = db.query(Courses).options(joinedload(Courses.category), joinedload(Courses.sub_group))
    userRole = str(current_user.role or "").lower()

    if userRole in ["admin", "staff", "headmajor"]:
        if departmentId:
            query = query.filter(Courses.department_id == departmentId)
    else:
        query = query.filter(Courses.department_id == current_user.department_id)

    offset = (page - 1) * size
    courses = query.order_by(Courses.course_code.asc()).offset(offset).limit(size).all()
    departmentNameMap = buildDepartmentNameMap(db, [course.department_id for course in courses])

    return [
        subjectPayloadToResponse(
            course,
            {
                "departmentName": departmentNameMap.get(course.department_id, ""),
                "department_name": departmentNameMap.get(course.department_id, ""),
                "majorName": departmentNameMap.get(course.department_id, ""),
                "major_name": departmentNameMap.get(course.department_id, ""),
            },
        )
        for course in courses
    ]


@router.get("/{course_id}")
async def get_course_by_id(course_id: int, db: Session = Depends(getDb), current_user: Users = Depends(get_current_user)):
    if current_user.role not in ["admin", "staff", "headmajor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้")

    course = db.query(Courses).options(joinedload(Courses.category), joinedload(Courses.sub_group)).filter(Courses.id == course_id).first()

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ไม่พบรายวิชารหัส ID: {course_id} ในระบบ")

    departmentNameMap = buildDepartmentNameMap(db, [course.department_id])
    return subjectPayloadToResponse(
        course,
        {
            "departmentName": departmentNameMap.get(course.department_id, ""),
            "department_name": departmentNameMap.get(course.department_id, ""),
            "majorName": departmentNameMap.get(course.department_id, ""),
            "major_name": departmentNameMap.get(course.department_id, ""),
        },
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_course(data: CourseCreate, db: Session = Depends(getDb), current_user=Depends(check_admin_staff_role)):
    existing_course = db.query(Courses).filter(Courses.course_code == data.course_code).first()

    if existing_course:
        raise HTTPException(status_code=400, detail=f"รหัสวิชา {data.course_code} มีอยู่ในระบบแล้ว ไม่สามารถสร้างซ้ำได้")

    new_course = Courses(**data.model_dump())
    db.add(new_course)

    try:
        db.commit()
        db.refresh(new_course)

        return {
            "status": "success",
            "message": "เพิ่มรายวิชาสำเร็จเรียบร้อยแล้ว!",
            "data": {
                "id": new_course.id,
                "course_code": new_course.course_code,
                "course_name_th": new_course.course_name_th,
            },
        }
    except Exception as e:
        db.rollback()
        print(f"Error logic: {str(e)}")
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดทางเทคนิคในการบันทึกข้อมูล")


@router.put("/{course_id}", response_model=CourseUpdate)
async def update_course(course_id: int, course_data: CourseUpdate, db: Session = Depends(getDb), current_user: Users = Depends(get_current_user)):
    if current_user.role not in ["admin", "staff", "headmajor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้")

    db_course = db.query(Courses).filter(Courses.id == course_id).first()

    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบข้อมูลวิชาที่ต้องการแก้ไข")

    update_data = course_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_course, key, value)

    try:
        db.commit()
        db.refresh(db_course)
        return db_course
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการอัปเดต: {str(e)}")


@router.delete("/{course_id}")
async def delete_course(course_id: int, db: Session = Depends(getDb), current_user: Users = Depends(get_current_user)):
    if current_user.role not in ["admin", "staff"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="เฉพาะเจ้าหน้าที่หรือผู้ดูแลระบบเท่านั้นที่ทำรายการนี้ได้")

    db_course = db.query(Courses).filter(Courses.id == course_id).first()

    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ไม่พบข้อมูลวิชาที่ต้องการลบ")

    try:
        db.delete(db_course)
        db.commit()
        return {"detail": f"ลบรายวิชา ID {course_id} สำเร็จ"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการลบ: {str(e)}")