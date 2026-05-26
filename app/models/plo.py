from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from app.Interface.sql_db import base
from app.models.base import TimestampMixin

sub_plo_course_association = Table(
    "sub_plo_courses",
    base.metadata,
    Column("id", Integer, primary_key=True),
    Column("sub_plo_id", Integer, ForeignKey("sub_plos.id", ondelete="CASCADE")),
    Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE")),
)
sub_plo_courses = sub_plo_course_association

class PLOs(base):
    __tablename__ = "plos"
    id = Column(Integer, primary_key=True)
    plo_code = Column(String(10), unique=True) # PLO1 - PLO8
    plo_name_thai = Column(Text)
    
    sub_plos = relationship("SubPLOs", back_populates="parent_plo")

class SubPLOs(base, TimestampMixin):
    __tablename__ = "sub_plos"
    id = Column(Integer, primary_key=True)
    sub_plo_code = Column(String(20))
    sub_plo_name_thai = Column(Text)
    plo_id = Column(Integer, ForeignKey("plos.id"))

    parent_plo = relationship("PLOs", back_populates="sub_plos")
    courses = relationship("Courses", secondary=sub_plo_course_association, back_populates="sub_plos")
