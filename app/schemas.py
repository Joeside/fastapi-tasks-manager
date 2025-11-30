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
    # optional fields
    tag: Optional[str] = None
    position: Optional[int] = None
    quadrant: Optional[int] = None
    # v0.5: recurrence fields
    recurrence_pattern: Optional[str] = None  # "daily", "weekly", "monthly"
    recurrence_end_date: Optional[date] = None


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
    tag: Optional[str] = None
    position: Optional[int] = None
    quadrant: Optional[int] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[date] = None


class TaskOut(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    quadrant: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TaskPositionUpdate(BaseModel):
    position: Optional[int]


class TaskQuadrantUpdate(BaseModel):
    quadrant: Optional[int]


class TaskReorderItem(BaseModel):
    id: int
    position: Optional[int]


class TaskBulkReorder(BaseModel):
    items: list[TaskReorderItem]


# v0.5: Subtask schemas
class SubtaskBase(BaseModel):
    title: str
    status: str = "todo"
    position: Optional[int] = None


class SubtaskCreate(SubtaskBase):
    pass


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    position: Optional[int] = None


class SubtaskOut(SubtaskBase):
    id: int
    task_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Subtask bulk reorder
class SubtaskReorderItem(BaseModel):
    id: int
    position: Optional[int]


class SubtaskBulkReorder(BaseModel):
    items: list[SubtaskReorderItem]
