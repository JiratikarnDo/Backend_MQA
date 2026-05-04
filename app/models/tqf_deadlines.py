from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from app.Interface.sql_db import base
from app.models.base import TimestampMixin

class TQFDeadlines(base, TimestampMixin):
    __tablename__ = "tqf_deadlines"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tqf_type = Column(String(50), nullable=False)   # ประเภทเอกสาร (มคอ.3, มคอ.5)
    semester = Column(Integer, nullable=False)      # ภาคการศึกษา (1, 2, 3)
    academic_year = Column(Integer, nullable=False) # ปีการศึกษา (เช่น 2569)
    
    start_date = Column(DateTime, nullable=False)   # วันเปิดระบบ
    end_date = Column(DateTime, nullable=False)     # วันปิดระบบ
    
    is_active = Column(Boolean, default=True)       # เอาไว้เปิด-ปิดการใช้งานรอบนี้