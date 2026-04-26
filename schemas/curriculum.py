from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from schemas.organization import DepartmentResponse

class CurriculumDepartmentResponse(BaseModel):
    id: int
    curriculum_id: int
    department_id: int
    department: Optional[DepartmentResponse] = None
    model_config = ConfigDict(from_attributes=True)

class CurriculumBase(BaseModel):
    curriculum_level: Optional[str] = None
    curriculum_code: Optional[str] = None
    curriculum_name_thai: Optional[str] = None
    curriculum_name_english: Optional[str] = None
    status: Optional[str] = "draft"

class CurriculumCreate(CurriculumBase):
    department_ids: List[int] = []


class CurriculumUpdate(CurriculumBase):
    department_ids: Optional[List[int]] = None 
    model_config = ConfigDict(from_attributes=True)

class CurriculumResponse(CurriculumBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    shared_departments: List[CurriculumDepartmentResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class CurriculumResponseAll(CurriculumBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)