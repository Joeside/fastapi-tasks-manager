from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/", response_model=List[schemas.TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    urgent: Optional[bool] = None,
    important: Optional[bool] = None,
    q: Optional[str] = None,
    tag: Optional[str] = None,
    sort: Optional[str] = None,
):
    return crud.get_tasks(
        db, status=status, urgent=urgent, important=important, q=q, tag=tag, sort=sort
    )


@router.post("/", response_model=schemas.TaskOut)
def create_task(task_in: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task_in)


@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_one_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_one_task(
    task_id: int, task_in: schemas.TaskUpdate, db: Session = Depends(get_db)
):
    task = crud.update_task(db, task_id, task_in)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
def delete_one_task(task_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_task(db, task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}
