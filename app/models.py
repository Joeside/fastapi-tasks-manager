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
    # new fields
    tag = Column(String, nullable=True)
    position = Column(Integer, nullable=True)
    # store quadrant as integer 1..4 (Eisenhower quadrant)
    quadrant = Column(Integer, nullable=True)
    status = Column(String, default="todo")  # "todo" / "done"

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime, nullable=True)
