from pydantic import BaseModel, ConfigDict
from typing import Optional
from schemas.organization import DepartmentResponse, DepartmentResponseSimple

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
    prefixname: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department_id: Optional[int] = None
    role: str
    email: str
    department: Optional[DepartmentResponseSimple] = None

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: str
    prefixname: Optional[str] = None
    first_name: str
    last_name: str
    department_id: int

class UserUpdateInfo(BaseModel):
    prefixname: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

class UserUpdateDepartment(BaseModel):
    department_id: int

class UserUpdateRole(BaseModel):
    role: str