from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from .course import CourseResponse

class CurriculumSubjectBase(BaseModel):
    course_id: int
    subject_group: Optional[str] = None
    subgroup: Optional[str] = None
    course_line: Optional[str] = None
    year_level: Optional[int] = None
    semester: Optional[int] = None

class CurriculumSubjectCreate(CurriculumSubjectBase):
    curriculum_id: int # ใช้ตอนเจ้าหน้าที่กดเลือกวิชาลงหลักสูตร

class CurriculumSubjectUpdate(BaseModel):
    subject_group: Optional[str] = None
    subgroup: Optional[str] = None
    course_line: Optional[str] = None
    year_level: Optional[int] = None
    semester: Optional[int] = None

class CurriculumSubjectResponse(CurriculumSubjectBase):
    id: int
    curriculum_id: int
    course: Optional[CourseResponse] = None 

    model_config = ConfigDict(from_attributes=True)


class CurriculumBase(BaseModel):
    curriculum_code: str
    curriculum_name_thai: str
    curriculum_name_english: Optional[str] = None

class CurriculumCreate(CurriculumBase):
    pass

class CurriculumUpdate(BaseModel):
    curriculum_code: Optional[str] = None
    curriculum_name_thai: Optional[str] = None
    curriculum_name_english: Optional[str] = None

class CurriculumResponse(CurriculumBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    subjects: List[CurriculumSubjectResponse] = []

    model_config = ConfigDict(from_attributes=True)