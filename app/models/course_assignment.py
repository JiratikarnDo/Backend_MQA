from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.Interface.sql_db import base


class CourseTeacherAssignment(base):
    __tablename__ = "course_teacher_assignments"
    __table_args__ = (
        UniqueConstraint("requested_course_item_id", "teacher_id", name="uq_course_teacher_assignment"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    requested_course_item_id = Column(
        Integer,
        ForeignKey("requested_course_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    requested_course_item = relationship("RequestedCourseItem", back_populates="teacher_assignments")
    teacher = relationship("Users", foreign_keys=[teacher_id])
    assigned_by = relationship("Users", foreign_keys=[assigned_by_id])
