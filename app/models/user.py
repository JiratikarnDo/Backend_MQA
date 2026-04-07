from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.Interface.sql_db import base

class User(base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    teacher_id = Column(String(50), nullable=False) 
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="teacher")
    created_at = Column(DateTime(timezone=True), server_default=func.now())