from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    urgent: bool
    important: bool
    due_date: Optional[str] = None  # "YYYY-MM-DD"
    status: str = "todo"            # "todo" / "done"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    urgent: Optional[bool] = None
    important: Optional[bool] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    completed_at: Optional[datetime] = None

class TaskOut(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True
