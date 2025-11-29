from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date
from datetime import datetime, timezone
from .database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    urgent = Column(Boolean, default=False)
    important = Column(Boolean, default=False)

    due_date = Column(Date, nullable=True)  # stored as date (YYYY-MM-DD)
    status = Column(String, default="todo")  # "todo" / "done"

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime, nullable=True)
