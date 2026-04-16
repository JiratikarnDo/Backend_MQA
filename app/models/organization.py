from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.Interface.sql_db import base
from app.models.timestamp import TimestampMixin
from app.models.users import Users
from sqlalchemy.orm import relationship

class Faculties(base , TimestampMixin):
    __tablename__ = "faculties"
    id = Column(Integer, primary_key=True, index=True)
    faculty_name = Column(String(255), unique=True, nullable=False)

    departments = relationship("Departments", back_populates="faculty")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Departments(base , TimestampMixin):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculties.id", ondelete="CASCADE"))
    department_name = Column(String(255), nullable=False) 
    
    faculty = relationship("Faculties", back_populates="departments")
    
    users = relationship("Users", back_populates="department")

    created_at = Column(DateTime(timezone=True), server_default=func.now())