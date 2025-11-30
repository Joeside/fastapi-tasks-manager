from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_subtasks_api_flow():
    # Create a parent task
    r = client.post(
        "/api/tasks/",
        json={"title": "parent for subtasks", "urgent": False, "important": True},
    )
    assert r.status_code == 200
    task = r.json()

    # Create two subtasks
    s1 = client.post(f"/api/tasks/{task['id']}/subtasks/", json={"title": "sub 1"})
    assert s1.status_code == 200
    s2 = client.post(f"/api/tasks/{task['id']}/subtasks/", json={"title": "sub 2"})
    assert s2.status_code == 200

    # List subtasks
    lst = client.get(f"/api/tasks/{task['id']}/subtasks/")
    assert lst.status_code == 200
    subs = lst.json()
    assert len(subs) >= 2

    # Update subtask status
    sid = subs[0]["id"]
    u = client.put(f"/api/tasks/{task['id']}/subtasks/{sid}", json={"status": "done"})
    assert u.status_code == 200
    assert u.json()["status"] == "done"

    # Reorder subtasks
    items = []
    # reverse current order
    for idx, s in enumerate(reversed(subs), start=1):
        items.append({"id": s["id"], "position": idx})
    rr = client.post(f"/api/tasks/{task['id']}/subtasks/reorder", json={"items": items})
    assert rr.status_code == 200

    # Delete subtask
    delr = client.delete(f"/api/tasks/{task['id']}/subtasks/{sid}")
    assert delr.status_code == 200
