from datetime import date, datetime, timedelta, timezone
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


def test_crud_lifecycle_and_stats():
    db = create_session()

    # create a few tasks
    t1 = schemas.TaskCreate(
        title="Task 1",
        description="First",
        urgent=True,
        important=True,
        due_date=date.today(),
        status="todo",
    )
    t2 = schemas.TaskCreate(
        title="Task 2",
        description="Second",
        urgent=False,
        important=True,
        due_date=None,
        status="todo",
    )
    t3 = schemas.TaskCreate(
        title="Task 3",
        description="Third",
        urgent=True,
        important=False,
        due_date=date.today() + timedelta(days=2),
        status="todo",
    )

    task1 = crud.create_task(db, t1)
    task2 = crud.create_task(db, t2)
    crud.create_task(db, t3)

    assert crud.get_tasks_count(db) == 3

    # get_tasks basic
    all_tasks = crud.get_tasks(db)
    assert len(all_tasks) == 3

    # get_task
    fetched = crud.get_task(db, task1.id)
    assert fetched.title == "Task 1"

    # update_task -> mark done and check completed_at
    upd = schemas.TaskUpdate(status="done")
    updated = crud.update_task(db, task1.id, upd)
    assert updated is not None
    assert updated.status == "done"
    assert updated.completed_at is not None

    # completed since (use a time in the past)
    now_utc = datetime.now(timezone.utc)
    since = now_utc - timedelta(days=1)
    done_since = crud.get_completed_since_count(db, since=since)
    assert done_since >= 1

    # eisenhower stats
    stats_all = crud.get_eisenhower_stats(db)
    assert stats_all["q1"] >= 0
    assert stats_all["q2"] >= 0
    assert stats_all["q3"] >= 0
    assert stats_all["q4"] >= 0

    # general stats
    general = crud.get_general_stats(db)
    assert general["total"] == 3
    assert isinstance(general["done"], int)

    # delete
    ok = crud.delete_task(db, task2.id)
    assert ok is True
    assert crud.get_tasks_count(db) == 2

    db.close()
