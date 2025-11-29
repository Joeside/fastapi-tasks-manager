from datetime import date, datetime
from app.database import SessionLocal
from app.models import Task


def parse_due(d):
    if d is None:
        return None
    if isinstance(d, date):
        return d
    try:
        # accept 'YYYY-MM-DD' or similar ISO formats
        return datetime.strptime(str(d), "%Y-%m-%d").date()
    except Exception:
        return None


def main():
    db = SessionLocal()
    try:
        tasks = db.query(Task).all()
        updated = 0
        for t in tasks:
            new_date = parse_due(t.due_date)
            if new_date != t.due_date:
                t.due_date = new_date
                updated += 1
        if updated:
            db.commit()
        print(f"Processed {len(tasks)} tasks, updated {updated} rows.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
