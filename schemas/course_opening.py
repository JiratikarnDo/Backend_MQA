from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import date, datetime


class RequestedCourseItemBase(BaseModel):
    year_level: int = Field(..., ge=1, le=4)
    course_id: int = Field(..., description="ID ของวิชาจากตาราง courses")
    group_no: int = 1
    student_count: int = 0
    is_elective: bool = False
    is_science_related: bool = False
    is_humanities_related: bool = False
    note: Optional[str] = Field(None, examples=["ขอเปิดเป็นกรณีพิเศษ"])


class ResponsiblePersonBase(BaseModel):
    name: str
    signed_date: Optional[date] = None


class AdminSignatory(BaseModel):
    name: str
    signed_date: Optional[date] = None


class CourseOpeningCreateDraft(BaseModel):
    submission_times: Optional[int] = None
    semester: Optional[str] = None
    academic_year: Optional[int] = None
    curriculum_name: Optional[str] = None
    major_name: Optional[str] = None
    program_type: Optional[str] = None
    study_mode: Optional[str] = None
    campus: Optional[str] = None
    target_group: Optional[str] = None

    requested_courses: List[RequestedCourseItemBase] = []
    responsible_persons: List[ResponsiblePersonBase] = []

    head_of_department: Optional[AdminSignatory] = None
    vice_dean: Optional[AdminSignatory] = None
    dean: Optional[AdminSignatory] = None
    is_confirmed: bool = False

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "submission_times": 1,
                "semester": "ภาค 1",
                "academic_year": 2568,
                "curriculum_name": "หลักสูตรวิทยาศาสตรบัณฑิต",
                "major_name": "วิทยาการคอมพิวเตอร์",
                "program_type": "4 ปี",
                "study_mode": "ภาคปกติ",
                "campus": "บางพระ",
                "target_group": "BP",
                "requested_courses": [
                    {
                        "year_level": 1,
                        "course_id": 1,
                        "group_no": 1,
                        "student_count": 0,
                        "is_science_related": True,
                        "is_humanities_related": True,
                        "is_elective": False,
                        "note": "ขอเปิดเป็นกรณีพิเศษ",
                    }
                ],
                "responsible_persons": [
                    {
                        "name": "อาจารย์ ก",
                        "signed_date": "2026-05-06",
                    }
                ],
                "head_of_department": {
                    "name": "อาจารย์ ปวีรา เครือโสม",
                    "signed_date": "2026-05-06",
                },
                "vice_dean": {
                    "name": "ผศ. อภิรัตน์ ใจผ่อง",
                    "signed_date": "2026-05-06",
                },
                "dean": {
                    "name": "นาย สมเกตุ วรเทพนิตย์",
                    "signed_date": "2026-05-06",
                },
                "is_confirmed": True,
            }
        },
    )


class CourseOpeningResponse(BaseModel):
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RequestedCourseItemRead(BaseModel):
    id: int
    course_id: int
    course_code_snapshot: str
    course_name_snapshot: str
    credits_snapshot: str
    year_level: int
    group_no: int
    student_count: int
    is_elective: bool
    is_science_related: bool
    is_humanities_related: bool
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ResponsiblePersonRead(BaseModel):
    id: int
    name: str
    signed_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class CourseOpeningSummaryResponse(BaseModel):
    id: int
    submission_times: int
    semester: str
    academic_year: int
    curriculum_name: str
    major_name: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseOpeningDetailResponse(CourseOpeningSummaryResponse):
    program_type: str
    study_mode: str
    campus: str
    target_group: str
<<<<<<< HEAD
    
    head_dept_name: Optional[str]
    head_dept_signed: Optional[date]
    vice_dean_name: Optional[str]
    vice_dean_signed: Optional[date]
    dean_name: Optional[str]
    dean_signed: Optional[date]
=======
>>>>>>> 9f82b4de0139a51bee4a45457ab04c3a15c94434

    head_dept_name: Optional[str] = None
    head_dept_signed: Optional[date] = None
    vice_dean_name: Optional[str] = None
    vice_dean_signed: Optional[date] = None
    dean_name: Optional[str] = None
    dean_signed: Optional[date] = None

    requested_courses: List[RequestedCourseItemRead]
    responsible_persons: List[ResponsiblePersonRead]


class DeanActionRequest(BaseModel):
    status: str
    comment: Optional[str] = None