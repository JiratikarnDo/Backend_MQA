from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional
from datetime import datetime

# 1. Base Schema: รวมฟิลด์พื้นฐานทั้งหมด
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

# 2. Create Schema: สำหรับเจ้าหน้าที่กรอกข้อมูลใหม่
class CourseCreate(CourseBase):
    # เจ้าหน้าที่ต้องระบุได้เองว่าวิชานี้เป็นของแผนกไหน
    department_id: int 

# 3. Update Schema: สำหรับการแก้ไข
class CourseUpdate(CourseBase):
    department_id: Optional[int] = None

# 4. Response Schema: สำหรับส่งข้อมูลกลับไปโชว์ที่หน้าบ้าน
class CourseResponse(CourseBase):
    id: int
    department_id: int
    created_at: datetime
    update_at: Optional[datetime] = None

    @computed_field
    @property
    def credit_display(self) -> str:
        total = self.credit_total or 0
        lec = self.credit_lecture or 0
        lab = self.credit_lab or 0
        self_study = self.credit_self_study or 0
        return f"{total}({lec}-{lab}-{self_study})"

    model_config = ConfigDict(from_attributes=True)