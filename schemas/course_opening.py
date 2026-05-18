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
    submission_times: Optional[int]
    semester: Optional[str]
    academic_year: Optional[int]
    curriculum_name: Optional[str]
    major_name: Optional[str]
    program_type: Optional[str]
    study_mode: Optional[str]
    campus: Optional[str]
    target_group: Optional[str]

    requested_courses: List[RequestedCourseItemBase]
    responsible_persons: List[ResponsiblePersonBase]

    head_of_department: AdminSignatory
    vice_dean: AdminSignatory
    dean: AdminSignatory
    is_confirmed: bool

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
                        "is_science_related": True,
                        "is_humanities_related":True,
                        "is_elective": False,
                        "note": "ขอเปิดเป็นกรณีพิเศษ"
                    }
                ],
                "responsible_persons": [
                    {"name": "อาจารย์ ก", "signed_date": "2026-05-06"}
                ],
                "head_of_department": {
                    "name": "อาจารย์ ปวีรา เครือโสม",
                    "signed_date": "2026-05-06",
                },
                "vice_dean": {
                    "name": "ผศ. อภิรัตน์ ใจผ่อง",
                    "signed_date": "2026-05-06",
                },
                "dean": {"name": "นาย สมเกตุ วรเทพนิตย์", "signed_date": "2026-05-06"},
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
    note: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class ResponsiblePersonRead(BaseModel):
    id: int
    name: str
    signed_date: Optional[date]
    model_config = ConfigDict(from_attributes=True)

class CourseOpeningDetailResponse(BaseModel):
    id: int
    submission_times: int
    semester: str
    academic_year: int
    curriculum_name: str
    major_name: str
    program_type: str
    study_mode: str
    campus: str
    target_group: str
    status: str
    created_at: datetime
    
    head_dept_name: Optional[str]
    head_dept_signed: Optional[date]
    vice_dean_name: Optional[str]
    vice_dean_signed: Optional[date]
    dean_name: Optional[str]
    dean_signed: Optional[date]

    requested_courses: List[RequestedCourseItemRead]
    responsible_persons: List[ResponsiblePersonRead]

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
    
    # ผู้ลงนาม
    head_dept_name: Optional[str]
    head_dept_signed: Optional[date]
    vice_dean_name: Optional[str]
    vice_dean_signed: Optional[date]
    dean_name: Optional[str]
    dean_signed: Optional[date]

    requested_courses: list[RequestedCourseItemRead] 
    responsible_persons: list[ResponsiblePersonRead]

class DeanActionRequest(BaseModel):
    status: str 
    comment: Optional[str] = None