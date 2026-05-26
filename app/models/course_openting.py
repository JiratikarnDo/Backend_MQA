from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.Interface.sql_db import base

class CourseOpeningRequest(base):
    __tablename__ = "course_opening_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_times = Column(Integer, default=1)
    semester = Column(String(50), nullable=False)
    academic_year = Column(Integer, nullable=False)
    curriculum_name = Column(String(255), nullable=False)
    major_name = Column(String(255), nullable=False)
    program_type = Column(String(50))
    
    study_mode = Column(String(100))
    campus = Column(String(100))
    target_group = Column(String(50))
    
    status = Column(String(20), default="pending")
    user_id = Column(Integer, ForeignKey("users.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    head_dept_name = Column(String(255))
    head_dept_signed = Column(Date)
    vice_dean_name = Column(String(255))
    vice_dean_signed = Column(Date)
    dean_name = Column(String(255))
    dean_signed = Column(Date)
    note = Column(String(500), nullable=True)

    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    requested_courses = relationship("RequestedCourseItem", back_populates="request", cascade="all, delete-orphan")
    responsible_persons = relationship("CurriculumResponsiblePerson", back_populates="request", cascade="all, delete-orphan")

class RequestedCourseItem(base):
    __tablename__ = "requested_course_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("course_opening_requests.id"))
    
    course_id = Column(Integer, ForeignKey("courses.id"))
    year_level = Column(Integer)
    group_no = Column(Integer)
    student_count = Column(Integer)
    is_elective = Column(Boolean)
    is_science_related = Column(Boolean)
    is_humanities_related = Column(Boolean, default=False) 
    note = Column(String(255))

    course_code_snapshot = Column(String(20))
    course_name_snapshot = Column(String(255))
    credits_snapshot = Column(String(50))

    request = relationship("CourseOpeningRequest", back_populates="requested_courses")
    teacher_assignments = relationship("CourseTeacherAssignment", back_populates="requested_course_item", cascade="all, delete-orphan")

class CurriculumResponsiblePerson(base):
    __tablename__ = "curriculum_responsible_persons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("course_opening_requests.id"))
    name = Column(String(255))
    signed_date = Column(Date)

    request = relationship("CourseOpeningRequest", back_populates="responsible_persons")
