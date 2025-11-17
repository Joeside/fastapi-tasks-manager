from sqlalchemy.orm import Session
from datetime import datetime
from . import models, schemas

def create_task(db: Session, task_in: schemas.TaskCreate):
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

def get_tasks(db: Session):
    return db.query(models.Task).order_by(models.Task.created_at.desc()).all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def update_task(db: Session, task_id: int, task_in: schemas.TaskUpdate):
    task = get_task(db, task_id)
    if not task:
        return None

    for field, value in task_in.dict(exclude_unset=True).items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()

    if task.status == "done" and task.completed_at is None:
        task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int):
    task = get_task(db, task_id)
    if not task:
        return None

    db.delete(task)
    db.commit()
    return True
