from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional
from datetime import datetime


class CourseBase(BaseModel):
    course_code: Optional[str] = None
    course_level: Optional[str] = None
    course_name_th: Optional[str] = None
    course_name_en: Optional[str] = None

    credit_total: Optional[int]
    credit_lecture: Optional[int]
    credit_lab: Optional[int]
    credit_self_study: Optional[int]

    description_thai: Optional[str] = None
    description_english: Optional[str] = None
    prerequisite: Optional[str] = None
    corequisite: Optional[str] = None

    category_id: Optional[int] = None
    sub_group_id: Optional[int] = None
    subject_line: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "course_code": "CP102",
                "course_level": "ปริญญาตรี",
                "course_name_th": "โครงสร้างข้อมูลและอัลกอริทึม",
                "course_name_en": "Data Structures and Algorithms",
                "credit_total": 3,
                "credit_lecture": 3,
                "credit_lab": 0,
                "credit_self_study": 6,
                "description_thai": "ศึกษาโครงสร้างข้อมูลและประสิทธิภาพอัลกอริทึม",
                "description_english": "Study data structures and algorithm efficiency",
                "prerequisite": "CP101",
                "corequisite": "-",
                "category_id": 1,
                "sub_group_id": 1,
                "subject_line": "วิชาเฉพาะด้าน",
                "department_id": 1
            }
        }
    )


class CourseReponseAll(BaseModel):
    id: int
    course_code: Optional[str] = None
    course_level: Optional[str] = None
    course_name_th: Optional[str] = None
    course_name_en: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CourseCreate(CourseBase):
    department_id: int


class CourseUpdate(CourseBase):
    department_id: Optional[int] = None


class CourseResponse(CourseBase):
    id: int
    department_id: int
    department_name: str | None = None
    created_at: datetime
    update_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CourseUpdate(BaseModel):
    course_code: Optional[str] = None
    course_level: Optional[str] = None
    course_name_th: Optional[str] = None
    course_name_en: Optional[str] = None
    category_id: Optional[int] = None
    sub_group_id: Optional[int] = None
    subject_line: Optional[str] = None
    credit_total: Optional[int] = None
    credit_lecture: Optional[int] = None
    credit_lab: Optional[int] = None
    credit_self_study: Optional[int] = None
    description_thai: Optional[str] = None
    description_english: Optional[str] = None
    prerequisite: Optional[str] = None
    corequisite: Optional[str] = None
    department_id: Optional[int] = None
