from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CourseAssignmentRequest(BaseModel):
    teacher_ids: List[int] = Field(..., min_length=1)


class AssignedTeacherResponse(BaseModel):
    id: int
    teacher_id: int
    teacher_name: str
    teacher_role: str
    is_primary: bool
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class AssignableTeacherResponse(BaseModel):
    id: int
    email: str
    role: str
    prefixname: Optional[str] = None
    first_name: str
    last_name: str
    department_id: Optional[int] = None
    department_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ApprovedCourseAssignmentResponse(BaseModel):
    requested_course_item_id: int
    request_id: int
    level: Optional[str] = None
    curriculum_name: str
    major_name: str
    semester: str
    academic_year: int
    year_level: Optional[int] = None
    course_id: Optional[int] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    section_number: Optional[int] = None
    student_count: Optional[int] = None
    assignment_status: str
    assigned_teachers: List[AssignedTeacherResponse] = Field(default_factory=list)
    primary_teacher: Optional[AssignedTeacherResponse] = None


class CourseAssignmentSaveResponse(BaseModel):
    status: str
    message: str
    requested_course_item_id: int
    assigned_teachers: List[AssignedTeacherResponse]
    primary_teacher: Optional[AssignedTeacherResponse] = None
    updated_at: datetime
