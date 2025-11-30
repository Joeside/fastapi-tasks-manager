from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud
from ..database import get_db

router = APIRouter(prefix="/api/tasks/{task_id}/subtasks", tags=["subtasks"])


@router.post("/", response_model=schemas.SubtaskOut)
def create_subtask(
    task_id: int, subtask_in: schemas.SubtaskCreate, db: Session = Depends(get_db)
):
    """Create a new subtask for a task."""
    subtask = crud.create_subtask(db, task_id, subtask_in)
    if not subtask:
        raise HTTPException(status_code=404, detail="Parent task not found")
    return subtask


@router.get("/", response_model=List[schemas.SubtaskOut])
def list_subtasks(task_id: int, db: Session = Depends(get_db)):
    """Get all subtasks for a task."""
    return crud.get_subtasks(db, task_id)


@router.get("/{subtask_id}", response_model=schemas.SubtaskOut)
def get_subtask(task_id: int, subtask_id: int, db: Session = Depends(get_db)):
    """Get a single subtask."""
    subtask = crud.get_subtask(db, subtask_id)
    if not subtask or subtask.task_id != task_id:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return subtask


@router.put("/{subtask_id}", response_model=schemas.SubtaskOut)
def update_subtask(
    task_id: int,
    subtask_id: int,
    subtask_in: schemas.SubtaskUpdate,
    db: Session = Depends(get_db),
):
    """Update a subtask."""
    subtask = crud.update_subtask(db, subtask_id, subtask_in)
    if not subtask or subtask.task_id != task_id:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return subtask


@router.delete("/{subtask_id}")
def delete_subtask(task_id: int, subtask_id: int, db: Session = Depends(get_db)):
    """Delete a subtask."""
    subtask = crud.get_subtask(db, subtask_id)
    if not subtask or subtask.task_id != task_id:
        raise HTTPException(status_code=404, detail="Subtask not found")

    ok = crud.delete_subtask(db, subtask_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return {"ok": True}


@router.post("/reorder")
def reorder_subtasks(
    task_id: int, payload: schemas.SubtaskBulkReorder, db: Session = Depends(get_db)
):
    """Bulk reorder subtasks within a task."""
    updated = crud.set_subtask_positions_bulk(db, task_id, payload.items)
    return {"updated": [s.id for s in updated]}
