from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.Interface.sql_db import getDb
from app.dependencies.auth import get_current_user
from app.models.course_assignment import CourseTeacherAssignment
from app.models.course_openting import CourseOpeningRequest, RequestedCourseItem
from app.models.users import Users
from schemas.course_assignment import (
    ApprovedCourseAssignmentResponse,
    AssignableTeacherResponse,
    AssignedTeacherResponse,
    CourseAssignmentRequest,
    CourseAssignmentSaveResponse,
)

router = APIRouter(prefix="/course-assignment", tags=["Course Assignment"])


def build_course_assignment_response(item: RequestedCourseItem):
    assigned_teachers = []

    for assignment in sorted(item.teacher_assignments, key=lambda a: a.order_index):
        teacher = assignment.teacher
        teacher_name = " ".join(
            part for part in [teacher.prefixname, teacher.first_name, teacher.last_name] if part
        )

        assigned_teachers.append(AssignedTeacherResponse(
            id=assignment.id,
            teacher_id=assignment.teacher_id,
            teacher_name=teacher_name,
            teacher_role=teacher.role,
            is_primary=assignment.is_primary,
            order_index=assignment.order_index,
        ))

    primary_teacher = next((teacher for teacher in assigned_teachers if teacher.is_primary), None)

    return ApprovedCourseAssignmentResponse(
        course_id=item.id,
        request_id=item.request_id,
        level=item.request.program_type,
        curriculum_name=item.request.curriculum_name,
        major_name=item.request.major_name,
        semester=item.request.semester,
        academic_year=item.request.academic_year,
        year_level=item.year_level,
        master_course_id=item.course_id,
        course_code=item.course_code_snapshot,
        course_name=item.course_name_snapshot,
        section_number=item.group_no,
        student_count=item.student_count,
        assignment_status="assigned" if assigned_teachers else "pending",
        assigned_teachers=assigned_teachers,
        primary_teacher=primary_teacher,
    )


@router.get("/approved-courses", response_model=List[ApprovedCourseAssignmentResponse])
async def get_approved_courses_for_assignment(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    if current_user.role.lower() not in ["admin", "staff", "headmajor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="คุณไม่มีสิทธิ์ดูข้อมูลการมอบหมายรายวิชา",
        )

    query = db.query(RequestedCourseItem).join(CourseOpeningRequest).options(
        joinedload(RequestedCourseItem.request),
        joinedload(RequestedCourseItem.teacher_assignments).joinedload(CourseTeacherAssignment.teacher)
    ).filter(CourseOpeningRequest.status == "approved")

    if current_user.role.lower() not in ["admin", "staff"]:
        query = query.filter(CourseOpeningRequest.department_id == current_user.department_id)

    offset = (page - 1) * limit
    results = query.order_by(
        CourseOpeningRequest.created_at.desc(),
        RequestedCourseItem.id.asc()
    ).offset(offset).limit(limit).all()

    return [build_course_assignment_response(item) for item in results]


@router.get("/teachers", response_model=List[AssignableTeacherResponse])
async def get_assignable_teachers(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    user_role = str(current_user.role or "").strip().lower()

    if user_role not in ["admin", "staff", "headmajor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="คุณไม่มีสิทธิ์ดูรายชื่ออาจารย์สำหรับมอบหมายรายวิชา",
        )

    query = db.query(Users).options(joinedload(Users.department)).filter(
        Users.role.in_(["teacher", "headmajor"]),
        Users.department_id == current_user.department_id,
    )

    teachers = query.order_by(Users.first_name.asc(), Users.last_name.asc()).all()

    return [
        AssignableTeacherResponse(
            id=teacher.id,
            role=teacher.role,
            prefixname=teacher.prefixname,
            first_name=teacher.first_name,
            last_name=teacher.last_name,
            department_name=teacher.department.department_name if teacher.department else None,
        )
        for teacher in teachers
    ]


@router.get("/my-primary-courses", response_model=List[ApprovedCourseAssignmentResponse])
async def get_my_primary_assigned_courses(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    results = db.query(RequestedCourseItem).join(CourseTeacherAssignment).join(
        CourseOpeningRequest,
        RequestedCourseItem.request_id == CourseOpeningRequest.id
    ).options(
        joinedload(RequestedCourseItem.request),
        joinedload(RequestedCourseItem.teacher_assignments).joinedload(CourseTeacherAssignment.teacher)
    ).filter(
        CourseTeacherAssignment.teacher_id == current_user.id,
        CourseTeacherAssignment.is_primary.is_(True),
        CourseOpeningRequest.status == "approved",
    ).all()

    return [build_course_assignment_response(item) for item in results]


@router.get("/{course_id}", response_model=ApprovedCourseAssignmentResponse)
async def get_course_assignment_by_id(
    course_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    item = db.query(RequestedCourseItem).options(
        joinedload(RequestedCourseItem.request),
        joinedload(RequestedCourseItem.teacher_assignments).joinedload(CourseTeacherAssignment.teacher)
    ).filter(RequestedCourseItem.id == course_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="ไม่พบรายการรายวิชาที่ระบุ")

    if current_user.role.lower() not in ["admin", "staff", "headmajor", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="คุณไม่มีสิทธิ์ดูรายละเอียดการมอบหมายรายวิชานี้",
        )

    if current_user.role.lower() not in ["admin", "staff"]:
        if item.request.department_id != current_user.department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="คุณไม่มีสิทธิ์ดูข้อมูลรายวิชานอกสาขาของคุณ",
            )

        if current_user.role.lower() == "teacher":
            assigned_teacher_ids = [
                assignment.teacher_id for assignment in item.teacher_assignments
            ]
            if current_user.id not in assigned_teacher_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="คุณไม่มีสิทธิ์ดูรายละเอียดการมอบหมายรายวิชานี้",
                )

    return build_course_assignment_response(item)


@router.post("/{course_id}", response_model=CourseAssignmentSaveResponse)
async def create_course_assignments(
    course_id: int,
    data: CourseAssignmentRequest,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role.lower() != "headmajor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะหัวหน้าสาขาวิชาเท่านั้นที่สามารถมอบหมายอาจารย์ผู้สอนได้",
        )

    if not data.teacher_ids:
        raise HTTPException(status_code=400, detail="กรุณาระบุอาจารย์ผู้สอนอย่างน้อย 1 คน")

    return save_course_assignments(course_id, data, db, current_user)


@router.put("/{course_id}", response_model=CourseAssignmentSaveResponse)
async def update_course_assignments(
    course_id: int,
    data: CourseAssignmentRequest,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role.lower() != "headmajor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะหัวหน้าสาขาวิชาเท่านั้นที่สามารถมอบหมายอาจารย์ผู้สอนได้",
        )

    return save_course_assignments(course_id, data, db, current_user)


@router.delete("/{course_id}", response_model=CourseAssignmentSaveResponse)
async def clear_course_assignments(
    course_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    if current_user.role.lower() != "headmajor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะหัวหน้าสาขาวิชาเท่านั้นที่สามารถมอบหมายอาจารย์ผู้สอนได้",
        )

    data = CourseAssignmentRequest(teacher_ids=[])
    return save_course_assignments(course_id, data, db, current_user)


def save_course_assignments(
    course_id: int,
    data: CourseAssignmentRequest,
    db: Session,
    current_user: Users,
):
    item = db.query(RequestedCourseItem).options(
        joinedload(RequestedCourseItem.request)
    ).filter(RequestedCourseItem.id == course_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="ไม่พบรายการรายวิชาที่ระบุ")

    if item.request.status != "approved":
        raise HTTPException(status_code=400, detail="ต้องเป็นรายวิชาที่ผ่านการอนุมัติเปิดสอนแล้วเท่านั้น")

    if item.request.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ไม่สามารถมอบหมายอาจารย์ให้รายวิชานอกสาขาของคุณได้",
        )

    teacher_ids = list(dict.fromkeys(data.teacher_ids))
    if len(teacher_ids) != len(data.teacher_ids):
        raise HTTPException(status_code=400, detail="ไม่สามารถส่งรหัสอาจารย์ซ้ำในรายวิชาเดียวกันได้")

    if teacher_ids:
        teachers = db.query(Users).filter(Users.id.in_(teacher_ids)).all()
        teacher_map = {teacher.id: teacher for teacher in teachers}

        missing_teacher_ids = [
            teacher_id for teacher_id in teacher_ids if teacher_id not in teacher_map
        ]
        if missing_teacher_ids:
            raise HTTPException(status_code=400, detail=f"ไม่พบรหัสอาจารย์: {missing_teacher_ids}")

        invalid_teacher_ids = [
            teacher.id
            for teacher in teachers
            if teacher.department_id != current_user.department_id
            or teacher.role.lower() not in ["teacher", "headmajor"]
        ]
        if invalid_teacher_ids:
            raise HTTPException(
                status_code=400,
                detail=f"รหัสอาจารย์ไม่ถูกต้องหรือไม่ได้อยู่ในสาขานี้: {invalid_teacher_ids}",
            )

    try:
        db.query(CourseTeacherAssignment).filter(
            CourseTeacherAssignment.requested_course_item_id == course_id
        ).delete(synchronize_session=False)

        for index, teacher_id in enumerate(teacher_ids):
            db.add(CourseTeacherAssignment(
                requested_course_item_id=course_id,
                teacher_id=teacher_id,
                assigned_by_id=current_user.id,
                is_primary=index == 0,
                order_index=index,
            ))

        db.commit()

        assignments = db.query(CourseTeacherAssignment).options(
            joinedload(CourseTeacherAssignment.teacher)
        ).filter(
            CourseTeacherAssignment.requested_course_item_id == course_id
        ).order_by(CourseTeacherAssignment.order_index.asc()).all()

        assigned_teachers = []
        for assignment in assignments:
            teacher = assignment.teacher
            teacher_name = " ".join(
                part for part in [teacher.prefixname, teacher.first_name, teacher.last_name] if part
            )
            assigned_teachers.append(AssignedTeacherResponse(
                id=assignment.id,
                teacher_id=assignment.teacher_id,
                teacher_name=teacher_name,
                teacher_role=teacher.role,
                is_primary=assignment.is_primary,
                order_index=assignment.order_index,
            ))

        primary_teacher = next((teacher for teacher in assigned_teachers if teacher.is_primary), None)
        message = (
            "ลบการมอบหมายอาจารย์ผู้สอนสำเร็จ"
            if not assigned_teachers
            else "บันทึกการมอบหมายอาจารย์ผู้สอนสำเร็จ"
        )

        return CourseAssignmentSaveResponse(
            status="success",
            message=message,
            course_id=course_id,
            assigned_teachers=assigned_teachers,
            primary_teacher=primary_teacher,
            updated_at=datetime.now(timezone.utc),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการมอบหมายรายวิชา: {str(e)}")
