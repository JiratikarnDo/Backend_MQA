from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from app.Interface.sql_db import base
from app.models.timestamp import TimestampMixin

class SubjectCategory(base, TimestampMixin):
    __tablename__ = "subject_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    sub_groups = relationship("SubjectSubGroup", back_populates="category")


class SubjectSubGroup(base, TimestampMixin):
    __tablename__ = "subject_sub_groups"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("subject_categories.id", ondelete="CASCADE"))
    
    category = relationship("SubjectCategory", back_populates="sub_groups")
