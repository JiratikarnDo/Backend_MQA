from pydantic import BaseModel, ConfigDict
from typing import Optional
from schemas.organization import DepartmentResponse

class UserProfileResponse(BaseModel):
    id: int
    email: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[DepartmentResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department_id: Optional[int] = None
    role: str

    model_config = {"from_attributes": True}