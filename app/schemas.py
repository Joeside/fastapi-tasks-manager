from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    urgent: bool
    important: bool
    due_date: Optional[date] = None  # date (YYYY-MM-DD)
    status: str = "todo"  # "todo" / "done"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    urgent: Optional[bool] = None
    important: Optional[bool] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    completed_at: Optional[datetime] = None


class TaskOut(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
