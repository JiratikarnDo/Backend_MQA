from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.Interface.sql_db import base

class TQF5Main(base):
    __tablename__ = "tqf5_main"
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    documentData = Column(JSON, nullable=False)

    courseCode = Column(String(50))
    nameThai = Column(String(255))
    nameEng = Column(String(255))
    credits = Column(Integer)
    creditsDetail = Column(String(100))
    curriculum = Column(JSON)
    teachers = Column(JSON)
    semester = Column(Integer)
    year = Column(Integer)
    yearLevel = Column(Integer)
    groupNumber = Column(Integer)
    studentCount = Column(Integer)
    location = Column(String(255))
    pre = Column(Text)
    co = Column(Text)
    updatedDate = Column(Date)
    deviatedHours = Column(Text)
    uncoveredTopics = Column(Text)
    registered = Column(Integer)
    remaining = Column(Integer)
    withdrawn = Column(Integer)
    abnormalFactor = Column(Text)

    department_id = Column(Integer)
    status = Column(String(50), default="draft")
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column("createdAt", DateTime, server_default=func.now())
    updated_at = Column("updatedAt", DateTime, server_default=func.now(), onupdate=func.now())

    teachers_list = relationship("TQF5Teacher", back_populates="tqf5", cascade="all, delete-orphan")
    clo_results = relationship("TQF5CLOResult", back_populates="tqf5", cascade="all, delete-orphan")
    grades = relationship("TQF5Grade", back_populates="tqf5", cascade="all, delete-orphan")
    tolerances = relationship("TQF5Tolerance", back_populates="tqf5", cascade="all, delete-orphan")
    issues = relationship("TQF5Issue", back_populates="tqf5", cascade="all, delete-orphan")
    feedbacks = relationship("TQF5Feedback", back_populates="tqf5", cascade="all, delete-orphan")
    past_plans = relationship("TQF5PastPlan", back_populates="tqf5", cascade="all, delete-orphan")
    next_plans = relationship("TQF5NextPlan", back_populates="tqf5", cascade="all, delete-orphan")
    list_items = relationship("TQF5ListItem", back_populates="tqf5", cascade="all, delete-orphan")
    signers = relationship("TQF5Signer", back_populates="tqf5", cascade="all, delete-orphan")

class TQF5Teacher(base):
    __tablename__ = "tqf5_teachers"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    name = Column(String(255))
    tqf5 = relationship("TQF5Main", back_populates="teachers_list")

class TQF5CLOResult(base):
    __tablename__ = "tqf5_clo_results"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    clo = Column(Text)
    teach = Column(Text)
    assess = Column(Text)
    outcome = Column(Text)
    improve = Column(Text)
    tqf5 = relationship("TQF5Main", back_populates="clo_results")

class TQF5Grade(base):
    __tablename__ = "tqf5_grades"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    grade = Column(String(20))
    range = Column(String(50))
    count = Column(Integer)
    percent = Column(Float)
    tqf5 = relationship("TQF5Main", back_populates="grades")

class TQF5Tolerance(base):
    __tablename__ = "tqf5_tolerances"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    deviation = Column(Text)
    reason = Column(Text)
    tqf5 = relationship("TQF5Main", back_populates="tolerances")

class TQF5Issue(base):
    __tablename__ = "tqf5_issues"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    issue_type = Column(String(50))
    issue = Column(Text)
    impact = Column(Text)
    tqf5 = relationship("TQF5Main", back_populates="issues")

class TQF5Feedback(base):
    __tablename__ = "tqf5_feedbacks"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    feedback_type = Column(String(50))
    criticism = Column(Text)
    response = Column(Text)
    tqf5 = relationship("TQF5Main", back_populates="feedbacks")

class TQF5PastPlan(base):
    __tablename__ = "tqf5_past_plans"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    plan = Column(Text)
    result = Column(Text)
    tqf5 = relationship("TQF5Main", back_populates="past_plans")

class TQF5NextPlan(base):
    __tablename__ = "tqf5_next_plans"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    plan = Column(Text)
    deadline = Column(String(255))
    owner = Column(String(255))
    tqf5 = relationship("TQF5Main", back_populates="next_plans")

class TQF5ListItem(base):
    __tablename__ = "tqf5_list_items"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    item_type = Column(String(50))
    detail = Column(Text)
    tqf5 = relationship("TQF5Main", back_populates="list_items")

class TQF5Signer(base):
    __tablename__ = "tqf5_signers"
    id = Column(Integer, primary_key=True)
    tqf5_id = Column(Integer, ForeignKey("tqf5_main.id"))
    signer_type = Column(String(50))
    name = Column(String(255))
    signature = Column(String(255))
    signed_date = Column(Date)
    tqf5 = relationship("TQF5Main", back_populates="signers")
