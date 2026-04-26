from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.Interface.sql_db import base
from sqlalchemy.orm import relationship

from app.models.base import TimestampMixin, StatusMixin


class Curriculum(base , TimestampMixin , StatusMixin):
    __tablename__ = "curriculums"
    id = Column(Integer, primary_key=True, index=True)
    curriculum_level = Column(String(50), nullable=True)
    curriculum_code = Column(String(50), unique=True, nullable=True)
    curriculum_name_thai = Column(String(255), nullable=True)
    curriculum_name_english = Column(String(255), nullable=True)
    
    shared_departments = relationship("CurriculumDepartment", back_populates="curriculum")

class CurriculumDepartment(base, TimestampMixin):
    __tablename__ = "curriculum_departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    curriculum_id = Column(Integer, ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=True)

    curriculum = relationship("Curriculum", back_populates="shared_departments")
    department = relationship("Departments")