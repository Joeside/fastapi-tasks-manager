from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models, crud, schemas


def create_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    models.Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def test_recurrence_daily_creates_next_occurrence():
    db = create_session()
    today = date.today()
    t = schemas.TaskCreate(
        title="Recurring daily",
        description=None,
        urgent=False,
        important=False,
        due_date=today,
        status="todo",
        recurrence_pattern="daily",
    )
    task = crud.create_task(db, t)

    # complete it
    upd = schemas.TaskUpdate(status="done")
    crud.update_task(db, task.id, upd)

    # There should be a new task with due_date = today + 1 day
    all_tasks = crud.get_tasks(db)
    assert len(all_tasks) == 2
    next_due = today + timedelta(days=1)
    assert any(x.due_date == next_due and x.status == "todo" for x in all_tasks)
    db.close()


def test_recurrence_respects_end_date():
    db = create_session()
    today = date.today()
    end = today  # end today so next occurrence should not be created
    t = schemas.TaskCreate(
        title="Recurring with end",
        description=None,
        urgent=False,
        important=False,
        due_date=today,
        status="todo",
        recurrence_pattern="daily",
        recurrence_end_date=end,
    )
    task = crud.create_task(db, t)

    upd = schemas.TaskUpdate(status="done")
    crud.update_task(db, task.id, upd)

    all_tasks = crud.get_tasks(db)
    # Only the original task should exist
    assert len(all_tasks) == 1
    db.close()
