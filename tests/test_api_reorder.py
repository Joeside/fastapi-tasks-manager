from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def create_task_helper(title, urgent=False, important=False, tag=None):
    payload = {
        "title": title,
        "urgent": urgent,
        "important": important,
    }
    if tag is not None:
        payload["tag"] = tag
    r = client.post("/api/tasks/", json=payload)
    assert r.status_code == 200
    return r.json()


def test_patch_position_and_quadrant_and_bulk_reorder():
    # create three uniquely named tasks
    a = create_task_helper("api-test-a")
    b = create_task_helper("api-test-b")
    c = create_task_helper("api-test-c")

    # patch position for task a
    r = client.patch(f"/api/tasks/{a['id']}/position", json={"position": 999})
    assert r.status_code == 200
    assert r.json()["position"] == 999

    # patch quadrant for task b -> set to 1 (urgent+important)
    r2 = client.patch(f"/api/tasks/{b['id']}/quadrant", json={"quadrant": 1})
    assert r2.status_code == 200
    jb = r2.json()
    assert jb.get("quadrant") == 1
    assert jb.get("urgent") is True
    assert jb.get("important") is True

    # bulk reorder: set positions for a,b,c
    items = [
        {"id": a["id"], "position": 3},
        {"id": b["id"], "position": 1},
        {"id": c["id"], "position": 2},
    ]
    r3 = client.post("/api/tasks/reorder", json={"items": items})
    assert r3.status_code == 200
    res = r3.json()
    # should return a list with at least the three updated tasks
    assert isinstance(res, list)
    returned_ids = {t["id"] for t in res}
    assert {a["id"], b["id"], c["id"]}.issubset(returned_ids)

    # fetch tasks sorted by position and ensure ordering by position is correct
    r4 = client.get("/api/tasks/?sort=position")
    assert r4.status_code == 200
    tasks = r4.json()
    # find our three tasks and check their relative positions
    pos_map = {
        t["id"]: t.get("position")
        for t in tasks
        if t["id"] in {a["id"], b["id"], c["id"]}
    }
    assert pos_map[a["id"]] == 3
    assert pos_map[b["id"]] == 1
    assert pos_map[c["id"]] == 2
