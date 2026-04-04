from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    id: int
    email: EmailStr
    teacher_id: str
    full_name: str
    role: str

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True