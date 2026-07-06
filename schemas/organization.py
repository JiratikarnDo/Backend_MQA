from pydantic import BaseModel, ConfigDict
from typing import Optional

class FacultySimpleResponse(BaseModel):
    id: int
    faculty_name: str
    model_config = ConfigDict(from_attributes=True)

class DepartmentResponse(BaseModel):
    id: int
    department_name: str
    faculty: Optional[FacultySimpleResponse] = None 

    model_config = ConfigDict(from_attributes=True)


class DepartmentResponseSimple(BaseModel):
    id: int
    department_name: str
    faculty_id: Optional[int] = None
    faculty_name: Optional[str] = None 

    model_config = ConfigDict(from_attributes=True)