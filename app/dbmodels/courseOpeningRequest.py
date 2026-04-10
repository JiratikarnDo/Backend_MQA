from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.mysql import JSON

from app.Interface.sql_db import base


class courseOpeningRequest(base):
    __tablename__ = "courseopeningrequest"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    degreeLevel = Column(String(50), nullable=False)
    requestScope = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    confirmStatus = Column(String(50), nullable=False, default="notConfirm")
    documentData = Column(JSON, nullable=False)

    semester = Column(String(20), nullable=True)
    academicYear = Column(String(20), nullable=True)
    curriculumName = Column(String(255), nullable=True)
    majorName = Column(String(255), nullable=True)

    createdAt = Column(DateTime, nullable=False, server_default=func.now())
    updatedAt = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
