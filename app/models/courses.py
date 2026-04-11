from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, text
from sqlalchemy.orm import relationship
from app.Interface.sql_db import base

class Courses(base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    description_thai = Column(text, nullable=True)
    description_english = Column(text, nullable=True)
    subject_group = Column(String(255), nullable=True)
    subgroup = Column(String(255), nullable=True)
    course_line = Column(String(255), nullable=True)

    course_code = Column(String(20), unique=True, nullable=False)
    course_name_th = Column(String(255), nullable=False)
    credit_sum = Column(String(10), nullable=True)
    describe = Column(String(10), nullable=True)
    operation = Column(String(10), nullable=True)
    prerequisite = Column(String(255), nullable=True)
    corequisite = Column(String(255), nullable=True)

    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    

