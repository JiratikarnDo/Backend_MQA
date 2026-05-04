from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from app.Interface.sql_db import base
from app.models.base import TimestampMixin

class Courses(base, TimestampMixin):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_code = Column(String(20), unique=True, nullable=True)
    course_level = Column(String(100), nullable=True)
    course_name_th = Column(String(255), nullable=True)
    course_name_en = Column(String(255), nullable=True)

    category_id = Column(Integer, ForeignKey("subject_categories.id", ondelete="SET NULL"), nullable=True)
    sub_group_id = Column(Integer, ForeignKey("subject_sub_groups.id", ondelete="SET NULL"), nullable=True)
    subject_line = Column(String(255), nullable=True)

    credit_total = Column(Integer, nullable=True)
    credit_lecture = Column(Integer, nullable=True)
    credit_lab = Column(Integer, nullable=True)
    credit_self_study = Column(Integer, nullable=True)
    
    description_thai = Column(Text, nullable=True)
    description_english = Column(Text, nullable=True)
    
    prerequisite = Column(String(255), nullable=True)
    corequisite = Column(String(255), nullable=True)

    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)

    category = relationship("SubjectCategory")
    sub_group = relationship("SubjectSubGroup")
    sub_plos = relationship("SubPLOs", secondary="sub_plo_courses", back_populates="courses")
