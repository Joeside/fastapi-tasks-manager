from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timezone
from typing import Optional, List, Dict
from . import models, schemas


def create_task(db: Session, task_in: schemas.TaskCreate) -> models.Task:
    """Create a Task from a `schemas.TaskCreate` and persist it.

    Returns the newly created `models.Task`.
    """
    task = models.Task(
        title=task_in.title,
        description=task_in.description,
        urgent=task_in.urgent,
        important=task_in.important,
        due_date=task_in.due_date,
        status=task_in.status,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(
    db: Session,
    status: Optional[str] = None,
    urgent: Optional[bool] = None,
    important: Optional[bool] = None,
    q: Optional[str] = None,
    sort: Optional[str] = None,
) -> List[models.Task]:
    """Return a list of tasks filtered by the provided options.

    Filter parameters are optional; `sort` supports 'due_asc', 'due_desc',
    and 'created_desc' (default).
    """
    query = db.query(models.Task)

    if status:
        query = query.filter(models.Task.status == status)
    if urgent is not None:
        query = query.filter(models.Task.urgent == urgent)
    if important is not None:
        query = query.filter(models.Task.important == important)
    if q:
        search_term = f"%{q.lower()}%"
        query = query.filter(
            (func.lower(models.Task.title).like(search_term))
            | (func.lower(models.Task.description).like(search_term))
        )

    sort_key = sort or "created_desc"
    if sort_key == "due_asc":
        # Tâches sans date en premier, puis par date croissante
        query = query.order_by(
            models.Task.due_date.is_(None), models.Task.due_date.asc()
        )
    elif sort_key == "due_desc":
        # Tâches avec date en premier, par date décroissante
        query = query.order_by(models.Task.due_date.desc().nullslast())
    else:  # "created_desc"
        query = query.order_by(models.Task.created_at.desc())

    return query.all()


def get_tasks_count(db: Session) -> int:
    """Return total number of tasks as an integer."""
    return db.query(func.count(models.Task.id)).scalar()


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    """Retrieve one task by id or return None if not found."""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_general_stats(db: Session) -> Dict[str, int]:
    """Return general statistics: total tasks and number done."""
    result = db.query(
        func.count(models.Task.id).label("total"),
        func.sum(case((models.Task.status == "done", 1), else_=0)).label("done"),
    ).one()
    return {"total": result.total or 0, "done": result.done or 0}


def get_completed_since_count(db: Session, since: datetime) -> int:
    """Count tasks completed since the given datetime."""
    return (
        db.query(func.count(models.Task.id))
        .filter(models.Task.status == "done", models.Task.completed_at >= since)
        .scalar()
    )


def update_task(
    db: Session, task_id: int, task_in: schemas.TaskUpdate
) -> Optional[models.Task]:
    """Apply partial updates from `TaskUpdate` to a task and return it.

    Returns None if the task does not exist.
    """
    task = get_task(db, task_id)
    if not task:
        return None

    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    task.updated_at = datetime.now(timezone.utc)

    if task.status == "done" and task.completed_at is None:
        task.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> Optional[bool]:
    """Delete a task by id. Returns True if deleted, None if not found."""
    task = get_task(db, task_id)
    if not task:
        return None

    db.delete(task)
    db.commit()
    return True


def get_eisenhower_stats(db: Session, status: Optional[str] = None) -> Dict[str, int]:
    """Return counts per Eisenhower quadrant (q1..q4).

    Uses explicit boolean comparisons for cross-database clarity.
    """
    query = db.query(
        func.sum(
            case(
                ((models.Task.urgent) & (models.Task.important), 1),
                else_=0,
            )
        ).label("q1"),
        func.sum(
            case(
                ((~models.Task.urgent) & (models.Task.important), 1),
                else_=0,
            )
        ).label("q2"),
        func.sum(
            case(
                ((models.Task.urgent) & (~models.Task.important), 1),
                else_=0,
            )
        ).label("q3"),
        func.sum(
            case(
                (((~models.Task.urgent) & (~models.Task.important)), 1),
                else_=0,
            )
        ).label("q4"),
    )

    if status:
        query = query.filter(models.Task.status == status)

    stats = query.one()

    return {
        "q1": stats.q1 or 0,
        "q2": stats.q2 or 0,
        "q3": stats.q3 or 0,
        "q4": stats.q4 or 0,
    }
