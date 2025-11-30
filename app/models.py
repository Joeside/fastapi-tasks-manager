from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
)
from sqlalchemy.orm import relationship
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

    # v0.5: recurrence fields
    recurrence_pattern = Column(
        String, nullable=True
    )  # "daily", "weekly", "monthly", or None
    recurrence_end_date = Column(
        Date, nullable=True
    )  # when to stop creating new occurrences

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime, nullable=True)

    # relationship to subtasks
    subtasks = relationship(
        "Subtask", back_populates="task", cascade="all, delete-orphan"
    )


class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    title = Column(String, nullable=False)
    status = Column(String, default="todo")  # "todo" / "done"
    position = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # relationship back to parent task
    task = relationship("Task", back_populates="subtasks")
