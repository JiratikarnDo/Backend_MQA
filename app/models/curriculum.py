from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.Interface.sql_db import base
from sqlalchemy.orm import relationship

from app.models.timestamp import TimestampMixin


class Curriculum(base , TimestampMixin):
    __tablename__ = "curriculums"
    id = Column(Integer, primary_key=True, index=True)
    curriculum_code = Column(String(50), unique=True, nullable=True)
    curriculum_name_thai = Column(String(255), nullable=True)
    curriculum_name_english = Column(String(255), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    
    curriculum_courses = relationship("CurriculumSubject", back_populates="curriculum")


class CurriculumSubject(base , TimestampMixin):
    __tablename__ = "curriculum_subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    curriculum_id = Column(Integer, ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    year_level = Column(Integer)  # เรียนปีไหน (1, 2, 3, 4)
    semester = Column(Integer)    # เรียนเทอมไหน (1, 2)
    subject_category = Column(String(100)) # หมวดวิชา (วิชาแกน, วิชาเลือก)
    

    curriculum = relationship("Curriculum", back_populates="curriculum_courses")
    course = relationship("Courses")