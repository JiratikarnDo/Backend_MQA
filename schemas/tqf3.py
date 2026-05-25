from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime

class InstructorBase(BaseModel):
    name: Optional[str] = None

class CLOBase(BaseModel):
    number: Optional[int] = None
    detail: Optional[str] = None

class DevelopmentBase(BaseModel):
    clo_number: Optional[int] = None
    teaching_strategy: Optional[str] = None
    evaluation_strategy: Optional[str] = None

class LessonPlanBase(BaseModel):
    week: Optional[int] = None
    topic: Optional[str] = None
    clos: Optional[str] = None
    hours: Optional[float] = None
    activities_media: Optional[str] = None
    instructor_name: Optional[str] = None

class EvaluationBase(BaseModel):
    activity: Optional[str] = None
    clo_number: Optional[str] = None
    evaluation_week: Optional[str] = None
    proportion_percent: Optional[float] = None

class TQF3Create(BaseModel):
    course_id: Optional[int] = None
    curriculum_name: Optional[str] = None
    course_category: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[int] = None
    year_level: Optional[str] = None
    section_group: Optional[str] = None
    student_count: Optional[int] = None
    location: Optional[str] = None
    pre_requisite: Optional[str] = None
    co_requisite: Optional[str] = None
    updated_at: Optional[datetime] = None
    course_description: Optional[str] = None
    objectives: Optional[str] = None
    plo_mapping: Optional[str] = None
    lecture_hours: Optional[float] = None
    practice_hours: Optional[float] = None
    self_study_hours: Optional[float] = None
    contact_detail: Optional[str] = None
    agreements: Optional[str] = None
    integration_detail: Optional[str] = None
    main_textbooks: Optional[str] = None
    references: Optional[str] = None
    
    instructors: Optional[List[InstructorBase]] = []
    clos: Optional[List[CLOBase]] = []
    development_plans: Optional[List[DevelopmentBase]] = []
    lesson_plans: Optional[List[LessonPlanBase]] = []
    evaluation_plans: Optional[List[EvaluationBase]] = []

    model_config = ConfigDict(
        str_strip_whitespace=True, 
        extra='forbid',
        json_schema_extra={
            "example": {
                "course_id": 1,
                "curriculum_name": "บริหารธุรกิจบัณฑิต สาขาวิชาระบบสารสนเทศ",
                "course_category": "วิชาเฉพาะด้าน",
                "semester": "1/2569",
                "academic_year": 2569,
                "year_level": "ปี 2",
                "section_group": "IS.267",
                "student_count": 45,
                "location": "อาคารคณะบริหารธุรกิจ มทร.ตะวันออก",
                "updated_at": "2026-05-12T20:34:02",
                "course_description": "ศึกษาเกี่ยวกับระบบฐานข้อมูล การออกแบบ Schema และการใช้งานคำสั่ง SQL เบื้องต้น",
                "objectives": "เพื่อให้นักศึกษาสามารถออกแบบและพัฒนาระบบฐานข้อมูลได้",
                "lecture_hours": 3.0,
                "practice_hours": 0.0,
                "self_study_hours": 6.0,
                "instructors": [
                    {"name": "อ.สมชาย สายคอม"},
                    {"name": "ดร.สมหญิง รักเรียน"}
                ],
                "clos": [
                    {"number": 1, "detail": "สามารถอธิบายหลักการของฐานข้อมูลเชิงสัมพันธ์ได้"},
                    {"number": 2, "detail": "สามารถเขียนคำสั่ง SQL เพื่อจัดการข้อมูลได้"}
                ],
                "lesson_plans": [
                    {
                        "week": 1,
                        "topic": "แนะนำรายวิชาและพื้นฐานฐานข้อมูล",
                        "clos": "1",
                        "hours": 3,
                        "activities_media": "บรรยายประกอบสไลด์",
                        "instructor_name": "อ.สมชาย สายคอม"
                    }
                ],
                "evaluation_plans": [
                    {
                        "activity": "สอบกลางภาค",
                        "clo_number": "1,2",
                        "evaluation_week": "9",
                        "proportion_percent": 30
                    },
                    {
                        "activity": "สอบปลายภาค",
                        "clo_number": "1,2",
                        "evaluation_week": "17",
                        "proportion_percent": 40
                    }
                ],
                "main_textbooks": "หนังสือการออกแบบฐานข้อมูล โดย รศ.ดร. มานะ อุตสาหะ",
                "references": "www.postgresql.org/docs"
            }
        }
    )


class InstructorResponse(InstructorBase):
    id: int
    model_config = {"from_attributes": True}

class CLOResponse(CLOBase):
    id: int
    model_config = {"from_attributes": True}

class DevelopmentResponse(DevelopmentBase):
    id: int
    model_config = {"from_attributes": True}

class LessonPlanResponse(LessonPlanBase):
    id: int
    model_config = {"from_attributes": True}

class EvaluationResponse(EvaluationBase):
    id: int
    model_config = {"from_attributes": True}

class TQF3Response(BaseModel):
    id: int
    course_id: Optional[int] = None

    course_code_snap: Optional[str] = None
    course_name_th_snap: Optional[str] = None
    course_name_en_snap: Optional[str] = None
    credits_snap: Optional[str] = None

    curriculum_name: Optional[str] = None
    course_category: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[int] = None
    year_level: Optional[str] = None
    section_group: Optional[str] = None
    student_count: Optional[int] = None
    location: Optional[str] = None
    pre_requisite: Optional[str] = None
    co_requisite: Optional[str] = None
    updated_at: Optional[datetime] = None
    course_description: Optional[str] = None
    objectives: Optional[str] = None
    plo_mapping: Optional[str] = None
    lecture_hours: Optional[float] = None
    practice_hours: Optional[float] = None
    self_study_hours: Optional[float] = None
    contact_detail: Optional[str] = None
    agreements: Optional[str] = None
    integration_detail: Optional[str] = None
    main_textbooks: Optional[str] = None
    references: Optional[str] = None

    instructors: Optional[List[InstructorResponse]] = []
    clos: Optional[List[CLOResponse]] = []
    development_plans: Optional[List[DevelopmentResponse]] = []
    lesson_plans: Optional[List[LessonPlanResponse]] = []
    evaluation_plans: Optional[List[EvaluationResponse]] = []

    model_config = {"from_attributes": True}