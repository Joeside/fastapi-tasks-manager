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


@router.patch("/{task_id}/position", response_model=schemas.TaskOut)
def update_task_position(
    task_id: int, pos_in: schemas.TaskPositionUpdate, db: Session = Depends(get_db)
):
    """Update only the `position` field of a task.

    Body: { "position": <int|null> }
    Returns the updated task or 404 if not found.
    """
    updated = crud.set_task_position(db, task_id, pos_in.position)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.patch("/{task_id}/quadrant", response_model=schemas.TaskOut)
def update_task_quadrant(
    task_id: int, q_in: schemas.TaskQuadrantUpdate, db: Session = Depends(get_db)
):
    """Update the `quadrant` of a task and adjust urgent/important flags accordingly.

    Body: { "quadrant": <1|2|3|4|null> }
    Returns the updated task or 404 if not found.
    """
    updated = crud.set_task_quadrant(db, task_id, q_in.quadrant)
    if not updated:
        raise HTTPException(
            status_code=404, detail="Task not found or invalid quadrant"
        )
    return updated


@router.post("/reorder", response_model=List[schemas.TaskOut])
def bulk_reorder(reorder: schemas.TaskBulkReorder, db: Session = Depends(get_db)):
    """Bulk update positions for multiple tasks. Accepts a payload `{"items": [{"id": 1, "position": 1}, ...]}`."""
    updated = crud.set_positions_bulk(db, reorder.items)
    return updated
