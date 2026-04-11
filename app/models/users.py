from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlmodel import ForeignKey
from app.Interface.sql_db import base
from sqlalchemy.orm import relationship


class Users(base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)

    department = relationship("Departments", back_populates="users")