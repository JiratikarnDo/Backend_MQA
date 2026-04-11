from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.Interface.sql_db import base
from sqlalchemy.orm import relationship


class Curriculum(base):
    __tablename__ = "curriculums"
    id = Column(Integer, primary_key=True, index=True)
    curriculum_code = Column(String(50), unique=True, nullable=True)
    curriculum_name_thai = Column(String(255), nullable=True)
    curriculum_name_english = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())