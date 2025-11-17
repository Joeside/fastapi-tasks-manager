from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from .database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    urgent = Column(Boolean, default=False)
    important = Column(Boolean, default=False)

    due_date = Column(String, nullable=True)   # "YYYY-MM-DD"
    status = Column(String, default="todo")    # "todo" / "done"

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
