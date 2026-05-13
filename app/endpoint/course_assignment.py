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

APPROVED_STATUS = "approved"
HEAD_MAJOR_ROLE = "headmajor"
ASSIGNABLE_TEACHER_ROLES = {"teacher", HEAD_MAJOR_ROLE}


def normalize_role(role: str | None) -> str:
    return (role or "").lower()


def require_head_major(current_user: Users):
    if normalize_role(current_user.role) != HEAD_MAJOR_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะหัวหน้าสาขาวิชาเท่านั้นที่สามารถมอบหมายอาจารย์ผู้สอนได้",
        )


def get_teacher_name(user: Users) -> str:
    name_parts = [user.prefixname, user.first_name, user.last_name]
    return " ".join(part for part in name_parts if part)


def get_primary_teacher(
    assigned_teachers: List[AssignedTeacherResponse],
) -> AssignedTeacherResponse | None:
    return next((teacher for teacher in assigned_teachers if teacher.is_primary), None)


def build_assigned_teacher_response(
    assignment: CourseTeacherAssignment,
) -> AssignedTeacherResponse:
    return AssignedTeacherResponse(
        id=assignment.id,
        teacher_id=assignment.teacher_id,
        teacher_name=get_teacher_name(assignment.teacher),
        teacher_role=assignment.teacher.role,
        is_primary=assignment.is_primary,
        order_index=assignment.order_index,
    )


def build_course_assignment_response(
    item: RequestedCourseItem,
) -> ApprovedCourseAssignmentResponse:
    request = item.request
    assignments = sorted(item.teacher_assignments, key=lambda item: item.order_index)
    assigned_teachers = [
        build_assigned_teacher_response(assignment) for assignment in assignments
    ]

    return ApprovedCourseAssignmentResponse(
        requested_course_item_id=item.id,
        request_id=item.request_id,
        level=request.program_type,
        curriculum_name=request.curriculum_name,
        major_name=request.major_name,
        semester=request.semester,
        academic_year=request.academic_year,
        year_level=item.year_level,
        course_id=item.course_id,
        course_code=item.course_code_snapshot,
        course_name=item.course_name_snapshot,
        section_number=item.group_no,
        student_count=item.student_count,
        assignment_status="assigned" if assigned_teachers else "pending",
        assigned_teachers=assigned_teachers,
        primary_teacher=get_primary_teacher(assigned_teachers),
    )


def build_assignable_teacher_response(teacher: Users) -> AssignableTeacherResponse:
    return AssignableTeacherResponse(
        id=teacher.id,
        email=teacher.email,
        role=teacher.role,
        prefixname=teacher.prefixname,
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        department_id=teacher.department_id,
        department_name=teacher.department.department_name if teacher.department else None,
    )


def get_requested_item_for_assignment(
    requested_course_item_id: int,
    current_user: Users,
    db: Session,
) -> RequestedCourseItem:
    requested_item = (
        db.query(RequestedCourseItem)
        .options(joinedload(RequestedCourseItem.request))
        .filter(RequestedCourseItem.id == requested_course_item_id)
        .first()
    )

    if not requested_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ไม่พบรายการรายวิชาที่ต้องการมอบหมาย",
        )

    if requested_item.request.status != APPROVED_STATUS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ต้องเป็นรายวิชาที่ผ่านการอนุมัติเปิดสอนแล้วเท่านั้น",
        )

    if requested_item.request.department_id != current_user.department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ไม่สามารถมอบหมายอาจารย์ให้รายวิชานอกสาขาของคุณได้",
        )

    return requested_item


def get_unique_teacher_ids(teacher_ids: List[int]) -> List[int]:
    unique_teacher_ids = list(dict.fromkeys(teacher_ids))
    if len(unique_teacher_ids) != len(teacher_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ไม่สามารถส่งรหัสอาจารย์ซ้ำในรายวิชาเดียวกันได้",
        )

    return unique_teacher_ids


def validate_assignable_teachers(
    teacher_ids: List[int],
    current_user: Users,
    db: Session,
) -> None:
    teachers = db.query(Users).filter(Users.id.in_(teacher_ids)).all()
    teacher_map = {teacher.id: teacher for teacher in teachers}

    missing_teacher_ids = [
        teacher_id for teacher_id in teacher_ids if teacher_id not in teacher_map
    ]
    if missing_teacher_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ไม่พบรหัสอาจารย์: {missing_teacher_ids}",
        )

    invalid_teacher_ids = [
        teacher.id
        for teacher in teachers
        if teacher.department_id != current_user.department_id
        or normalize_role(teacher.role) not in ASSIGNABLE_TEACHER_ROLES
    ]
    if invalid_teacher_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"รหัสอาจารย์ไม่ถูกต้องหรือไม่ได้อยู่ในสาขานี้: {invalid_teacher_ids}",
        )


def replace_course_assignments(
    requested_course_item_id: int,
    teacher_ids: List[int],
    assigned_by_id: int,
    db: Session,
) -> None:
    db.query(CourseTeacherAssignment).filter(
        CourseTeacherAssignment.requested_course_item_id == requested_course_item_id
    ).delete(synchronize_session=False)

    for index, teacher_id in enumerate(teacher_ids):
        db.add(
            CourseTeacherAssignment(
                requested_course_item_id=requested_course_item_id,
                teacher_id=teacher_id,
                assigned_by_id=assigned_by_id,
                is_primary=index == 0,
                order_index=index,
            )
        )


def get_assignments_by_course_item(
    requested_course_item_id: int,
    db: Session,
) -> List[CourseTeacherAssignment]:
    return (
        db.query(CourseTeacherAssignment)
        .options(joinedload(CourseTeacherAssignment.teacher))
        .filter(
            CourseTeacherAssignment.requested_course_item_id
            == requested_course_item_id
        )
        .order_by(CourseTeacherAssignment.order_index.asc())
        .all()
    )


@router.get("/approved-courses", response_model=List[ApprovedCourseAssignmentResponse])
async def get_approved_courses_for_assignment(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    require_head_major(current_user)

    offset = (page - 1) * limit
    results = (
        db.query(RequestedCourseItem)
        .join(CourseOpeningRequest)
        .options(
            joinedload(RequestedCourseItem.request),
            joinedload(RequestedCourseItem.teacher_assignments).joinedload(
                CourseTeacherAssignment.teacher
            ),
        )
        .filter(CourseOpeningRequest.status == APPROVED_STATUS)
        .filter(CourseOpeningRequest.department_id == current_user.department_id)
        .order_by(CourseOpeningRequest.created_at.desc(), RequestedCourseItem.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [build_course_assignment_response(item) for item in results]


@router.get("/teachers", response_model=List[AssignableTeacherResponse])
async def get_assignable_teachers(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
    search: str | None = Query(None),
):
    require_head_major(current_user)

    query = (
        db.query(Users)
        .options(joinedload(Users.department))
        .filter(Users.department_id == current_user.department_id)
        .filter(Users.role.in_(["teacher", "headMajor", "headmajor"]))
    )

    if search:
        keyword = f"%{search.strip()}%"
        query = query.filter(
            (Users.first_name.ilike(keyword))
            | (Users.last_name.ilike(keyword))
            | (Users.email.ilike(keyword))
        )

    teachers = query.order_by(Users.first_name.asc(), Users.last_name.asc()).all()
    return [build_assignable_teacher_response(teacher) for teacher in teachers]


@router.put("/{requested_course_item_id}", response_model=CourseAssignmentSaveResponse)
async def assign_teachers_to_course(
    requested_course_item_id: int,
    data: CourseAssignmentRequest,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    require_head_major(current_user)
    get_requested_item_for_assignment(requested_course_item_id, current_user, db)

    teacher_ids = get_unique_teacher_ids(data.teacher_ids)
    validate_assignable_teachers(teacher_ids, current_user, db)

    try:
        replace_course_assignments(
            requested_course_item_id=requested_course_item_id,
            teacher_ids=teacher_ids,
            assigned_by_id=current_user.id,
            db=db,
        )
        db.commit()

        assignments = get_assignments_by_course_item(requested_course_item_id, db)
        assigned_teachers = [
            build_assigned_teacher_response(assignment) for assignment in assignments
        ]

        return CourseAssignmentSaveResponse(
            status="success",
            message="บันทึกการมอบหมายอาจารย์ผู้สอนสำเร็จ",
            requested_course_item_id=requested_course_item_id,
            assigned_teachers=assigned_teachers,
            primary_teacher=get_primary_teacher(assigned_teachers),
            updated_at=datetime.now(timezone.utc),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการมอบหมายรายวิชา: {str(e)}",
        )


@router.delete("/{requested_course_item_id}", response_model=CourseAssignmentSaveResponse)
async def clear_course_assignments(
    requested_course_item_id: int,
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    require_head_major(current_user)
    get_requested_item_for_assignment(requested_course_item_id, current_user, db)

    try:
        db.query(CourseTeacherAssignment).filter(
            CourseTeacherAssignment.requested_course_item_id
            == requested_course_item_id
        ).delete(synchronize_session=False)
        db.commit()

        return CourseAssignmentSaveResponse(
            status="success",
            message="ลบการมอบหมายอาจารย์ผู้สอนสำเร็จ",
            requested_course_item_id=requested_course_item_id,
            assigned_teachers=[],
            primary_teacher=None,
            updated_at=datetime.now(timezone.utc),
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการลบการมอบหมายรายวิชา: {str(e)}",
        )


@router.get("/my-primary-courses", response_model=List[ApprovedCourseAssignmentResponse])
async def get_my_primary_assigned_courses(
    db: Session = Depends(getDb),
    current_user: Users = Depends(get_current_user),
):
    results = (
        db.query(RequestedCourseItem)
        .join(CourseTeacherAssignment)
        .join(CourseOpeningRequest, RequestedCourseItem.request_id == CourseOpeningRequest.id)
        .options(
            joinedload(RequestedCourseItem.request),
            joinedload(RequestedCourseItem.teacher_assignments).joinedload(
                CourseTeacherAssignment.teacher
            ),
        )
        .filter(CourseTeacherAssignment.teacher_id == current_user.id)
        .filter(CourseTeacherAssignment.is_primary.is_(True))
        .filter(CourseOpeningRequest.status == APPROVED_STATUS)
        .all()
    )

    return [build_course_assignment_response(item) for item in results]
