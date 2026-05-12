from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.Interface.sql_db import base

class TQF3Main(base):
    __tablename__ = "tqf3_main"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    
    # ส่วนที่ 1-3: Snapshot ข้อมูลวิชา
    course_code_snap = Column(String(20))
    course_name_th_snap = Column(String(255))
    course_name_en_snap = Column(String(255))
    credits_snap = Column(String(50))
    curriculum_name = Column(String(255))
    course_category = Column(String(100))

    # ส่วนที่ 5-11: ข้อมูลทั่วไป
    semester = Column(String(20))
    academic_year = Column(Integer)
    year_level = Column(String(50))
    section_group = Column(String(50))
    student_count = Column(Integer)
    location = Column(Text)
    pre_requisite = Column(Text, default="-")
    co_requisite = Column(Text, default="-")
    updated_at = Column(Date)
    course_description = Column(Text)
    objectives = Column(Text)
    plo_mapping = Column(Text)

    # ส่วนที่ 13: ชั่วโมงต่อสัปดาห์
    lecture_hours = Column(Float)
    practice_hours = Column(Float)
    self_study_hours = Column(Float)
    contact_detail = Column(Text)

    # ส่วนที่ 17-19: เอกสารและข้อตกลง
    agreements = Column(Text)
    integration_detail = Column(Text)
    main_textbooks = Column(Text)
    references = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

    instructors = relationship("TQF3Instructor", back_populates="tqf3", cascade="all, delete-orphan")
    clos = relationship("TQF3CLO", back_populates="tqf3", cascade="all, delete-orphan")
    development_plans = relationship("TQF3Development", back_populates="tqf3", cascade="all, delete-orphan")
    lesson_plans = relationship("TQF3LessonPlan", back_populates="tqf3", cascade="all, delete-orphan")
    evaluation_plans = relationship("TQF3Evaluation", back_populates="tqf3", cascade="all, delete-orphan")

class TQF3Instructor(base):
    __tablename__ = "tqf3_instructors"
    id = Column(Integer, primary_key=True)
    tqf3_id = Column(Integer, ForeignKey("tqf3_main.id"))
    name = Column(String(255))
    tqf3 = relationship("TQF3Main", back_populates="instructors")

class TQF3CLO(base):
    __tablename__ = "tqf3_clos"
    id = Column(Integer, primary_key=True)
    tqf3_id = Column(Integer, ForeignKey("tqf3_main.id"))
    number = Column(Integer)
    detail = Column(Text)
    tqf3 = relationship("TQF3Main", back_populates="clos")

class TQF3Development(base):
    __tablename__ = "tqf3_development"
    id = Column(Integer, primary_key=True)
    tqf3_id = Column(Integer, ForeignKey("tqf3_main.id"))
    clo_number = Column(Integer)
    teaching_strategy = Column(Text)
    evaluation_strategy = Column(Text)
    tqf3 = relationship("TQF3Main", back_populates="development_plans")

class TQF3LessonPlan(base):
    __tablename__ = "tqf3_lesson_plans"
    id = Column(Integer, primary_key=True)
    tqf3_id = Column(Integer, ForeignKey("tqf3_main.id"))
    week = Column(Integer)
    topic = Column(Text)
    clos = Column(String(100))
    hours = Column(Float)
    activities_media = Column(Text)
    instructor_name = Column(String(255))
    tqf3 = relationship("TQF3Main", back_populates="lesson_plans")

class TQF3Evaluation(base):
    __tablename__ = "tqf3_evaluation"
    id = Column(Integer, primary_key=True)
    tqf3_id = Column(Integer, ForeignKey("tqf3_main.id"))
    activity = Column(Text)
    clo_number = Column(String(100))
    evaluation_week = Column(String(50))
    proportion_percent = Column(Float)
    tqf3 = relationship("TQF3Main", back_populates="evaluation_plans")