from datetime import date, timedelta
from app.main import compute_due_status


def test_compute_due_status_none():
    assert compute_due_status(None) == "none"


def test_compute_due_status_overdue():
    yesterday = date.today() - timedelta(days=1)
    assert compute_due_status(yesterday) == "overdue"


def test_compute_due_status_today():
    today = date.today()
    assert compute_due_status(today) == "today"


def test_compute_due_status_soon_and_later():
    soon = date.today() + timedelta(days=3)
    later = date.today() + timedelta(days=10)
    assert compute_due_status(soon) == "soon"
    assert compute_due_status(later) == "later"
