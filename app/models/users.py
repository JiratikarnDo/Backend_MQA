from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlmodel import ForeignKey
from app.Interface.sql_db import base
from sqlalchemy.orm import relationship

from app.models.base import TimestampMixin

class Users(base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), nullable=False, default="teacher") 
    prefixname = Column(String(100), nullable=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    department = relationship("Departments", back_populates="users")