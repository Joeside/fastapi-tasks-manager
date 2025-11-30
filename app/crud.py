from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timezone
from typing import Optional, List, Dict
from . import models, schemas


def _compute_quadrant_val(urgent: bool, important: bool) -> int:
    """Return the Eisenhower quadrant number (1..4) from urgent/important flags."""
    if important and urgent:
        return 1
    if important and not urgent:
        return 2
    if not important and urgent:
        return 3
    return 4


def create_task(db: Session, task_in: schemas.TaskCreate) -> models.Task:
    """Create a Task from a `schemas.TaskCreate` and persist it.

    Returns the newly created `models.Task`.
    """
    # quadrant: respect provided value if present, otherwise compute from flags
    quadrant_val = None
    if getattr(task_in, "quadrant", None) is not None:
        quadrant_val = task_in.quadrant
    else:
        quadrant_val = _compute_quadrant_val(task_in.urgent, task_in.important)

    # Determine position: use provided value, otherwise set to next available
    provided_position = getattr(task_in, "position", None)
    if provided_position is None:
        max_pos = db.query(func.max(models.Task.position)).scalar()
        try:
            next_pos = (int(max_pos) if max_pos is not None else 0) + 1
        except Exception:
            next_pos = 1
        position_val = next_pos
    else:
        position_val = provided_position

    # Normalize tag to lowercase (case-insensitive handling)
    raw_tag = getattr(task_in, "tag", None)
    if raw_tag is None:
        tag_val = None
    else:
        t = raw_tag.strip()
        tag_val = t.lower() if t != "" else None

    task = models.Task(
        title=task_in.title,
        description=task_in.description,
        urgent=task_in.urgent,
        important=task_in.important,
        due_date=task_in.due_date,
        status=task_in.status,
        tag=tag_val,
        position=position_val,
        quadrant=quadrant_val,
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
    tag: Optional[str] = None,
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
    if tag:
        # Case-insensitive comparison: compare lower(tag) == lower(param)
        query = query.filter(func.lower(models.Task.tag) == tag.lower())

    sort_key = sort or "created_desc"
    if sort_key == "due_asc":
        # Tâches sans date en premier, puis par date croissante
        query = query.order_by(
            models.Task.due_date.is_(None), models.Task.due_date.asc()
        )
    elif sort_key == "due_desc":
        # Tâches avec date en premier, par date décroissante
        query = query.order_by(models.Task.due_date.desc().nullslast())
    elif sort_key == "position":
        # Trier par position croissante; les positions NULL restent en fin
        query = query.order_by(models.Task.position.asc().nullslast())
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

    dumped = task_in.model_dump(exclude_unset=True)
    for field, value in dumped.items():
        # Normalize tag on update as well
        if field == "tag":
            if value is None:
                norm = None
            else:
                s = str(value).strip()
                norm = s.lower() if s != "" else None
            setattr(task, field, norm)
        else:
            setattr(task, field, value)

    # If quadrant was not provided explicitly, recompute it from flags
    if "quadrant" not in dumped:
        try:
            task.quadrant = _compute_quadrant_val(task.urgent, task.important)
        except Exception:
            task.quadrant = None

    task.updated_at = datetime.now(timezone.utc)

    if task.status == "done" and task.completed_at is None:
        task.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)
    return task


def set_task_position(
    db: Session, task_id: int, position: Optional[int]
) -> Optional[models.Task]:
    """Set the `position` of a single task. Returns the updated task or None if not found."""
    task = get_task(db, task_id)
    if not task:
        return None

    # Allow nullable positions
    task.position = int(position) if position is not None else None
    task.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task


def set_task_quadrant(
    db: Session, task_id: int, quadrant: Optional[int]
) -> Optional[models.Task]:
    """Set the `quadrant` of a task and update urgent/important flags accordingly.

    Quadrant mapping (Eisenhower):
      1 -> urgent=True, important=True
      2 -> urgent=False, important=True
      3 -> urgent=True, important=False
      4 -> urgent=False, important=False

    Accepts None to clear quadrant (does not change flags in that case).
    """
    task = get_task(db, task_id)
    if not task:
        return None

    if quadrant is None:
        task.quadrant = None
    else:
        try:
            q = int(quadrant)
        except Exception:
            return None
        task.quadrant = q
        # Update flags based on quadrant
        if q == 1:
            task.urgent = True
            task.important = True
        elif q == 2:
            task.urgent = False
            task.important = True
        elif q == 3:
            task.urgent = True
            task.important = False
        else:
            task.urgent = False
            task.important = False

    task.updated_at = datetime.now(timezone.utc)
    # If marking done state not changed here
    db.commit()
    db.refresh(task)
    return task


def set_positions_bulk(db: Session, items: list) -> list:
    """Set positions for multiple tasks in a single transaction.

    `items` is an iterable of objects with attributes `id` and `position`.
    Returns the list of updated Task objects.
    """
    if not items:
        return []

    ids = [
        int(getattr(it, "id", it["id"])) if isinstance(it, dict) else int(it.id)
        for it in items
    ]
    # Fetch existing tasks
    tasks = db.query(models.Task).filter(models.Task.id.in_(ids)).all()
    task_map = {t.id: t for t in tasks}

    updated = []
    now = datetime.now(timezone.utc)
    for it in items:
        if isinstance(it, dict):
            tid = int(it.get("id"))
            pos = it.get("position")
        else:
            tid = int(it.id)
            pos = it.position

        task = task_map.get(tid)
        if not task:
            continue
        task.position = int(pos) if pos is not None else None
        task.updated_at = now
        updated.append(task)

    db.commit()
    # refresh updated tasks
    for t in updated:
        db.refresh(t)

    return updated


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
