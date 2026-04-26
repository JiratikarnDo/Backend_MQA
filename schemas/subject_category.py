from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class SubjectCategoryBase(BaseModel):
    name: Optional[str] = None


class SubjectCategoryCreate(SubjectCategoryBase):
    pass


class SubjectCategoryUpdate(BaseModel):
    name: Optional[str] = None


class SubjectCategoryResponse(SubjectCategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SubjectSubGroupBase(BaseModel):
    name: str
    category_id: int


class SubjectSubGroupCreate(SubjectSubGroupBase):
    pass


class SubjectSubGroupAll(SubjectSubGroupBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SubjectSubGroupResponse(SubjectSubGroupBase):
    id: int
    category: Optional[SubjectCategoryResponse] = None
    model_config = ConfigDict(from_attributes=True)


class SubjectSubGroupUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
