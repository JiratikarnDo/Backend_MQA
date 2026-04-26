
from sqlalchemy import DateTime, String, func
from sqlalchemy import Column


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StatusMixin:
    # draft, active, archived
    status = Column(String(20), default="draft", server_default="draft", nullable=False)