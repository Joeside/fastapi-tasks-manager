from fastapi import FastAPI, Request, Depends, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone, date
from typing import Optional
from urllib.parse import urlencode

from .database import Base, engine, get_db
from . import crud
from .routers import tasks as tasks_router


# Quadrants
def compute_quadrant(t) -> int:
    """
    Q1 : urgent & important
    Q2 : important seulement
    Q3 : urgent seulement
    Q4 : ni urgent ni important
    """
    if t.important and t.urgent:
        return 1
    elif t.important and not t.urgent:
        return 2
    elif not t.important and t.urgent:
        return 3
    else:
        return 4


def compute_due_status(due_date: Optional[date]) -> str:
    """
    Retourne l'un de :
    - "none"      : pas d'échéance
    - "overdue"   : en retard
    - "today"     : aujourd'hui
    - "soon"      : dans les 7 prochains jours
    - "later"     : plus tard
    """
    if not due_date:
        return "none"

    # due_date is a datetime.date object (or convertible to one)
    try:
        d = due_date
    except Exception:
        return "none"

    today = date.today()
    if d < today:
        return "overdue"
    if d == today:
        return "today"
    if d <= today + timedelta(days=7):
        return "soon"
    return "later"


# Crée les tables SQLite si elles n'existent pas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestion du Temps - MVP")

# servir /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# brancher les routes API REST
app.include_router(tasks_router.router)


@app.get("/list", response_class=HTMLResponse)
def page_list(
    request: Request,
    db: Session = Depends(get_db),
    status_f: Optional[str] = None,  # "all" | "todo" | "done"
    urgent_f: Optional[str] = None,  # "all" | "yes" | "no"
    important_f: Optional[str] = None,  # "all" | "yes" | "no"
    q: Optional[str] = None,  # recherche texte
    sort: Optional[str] = None,  # "created_desc" | "due_asc" | "due_desc"
):
    def yesno(val: Optional[str]):
        if val is None or val == "" or val == "all":
            return None
        return True if val == "yes" else False

    # --- Filtres et Tri ---
    status_val = status_f if status_f in {"todo", "done"} else None
    urgent_val = yesno(urgent_f)
    important_val = yesno(important_f)
    search_query = q.strip() if q else None
    sort_key = sort or "created_desc"

    tasks = crud.get_tasks(
        db,
        status=status_val,
        urgent=urgent_val,
        important=important_val,
        q=search_query,
        sort=sort_key,
    )
    total_count = crud.get_tasks_count(db)

    # --- Quadrant + statut d'échéance + regroupement ---
    overdue = []
    today_list = []
    soon = []
    later = []
    nodate = []
    done_tasks = []

    for t in tasks:
        t.quadrant = compute_quadrant(t)

        if t.status == "done":
            # On ne tient plus compte de la date due pour le classement principal
            t.due_status = "done"
            done_tasks.append(t)
            continue

        # Pour les tâches à faire, on calcule le statut d’échéance
        t.due_status = compute_due_status(t.due_date)

        if t.due_status == "overdue":
            overdue.append(t)
        elif t.due_status == "today":
            today_list.append(t)
        elif t.due_status == "soon":
            soon.append(t)
        elif t.due_status == "later":
            later.append(t)
        else:
            nodate.append(t)

    due_sections = [
        {"key": "overdue", "label": "En retard", "tasks": overdue},
        {"key": "today", "label": "Aujourd'hui", "tasks": today_list},
        {"key": "soon", "label": "Cette semaine", "tasks": soon},
        {"key": "later", "label": "Plus tard", "tasks": later},
        {"key": "none", "label": "Sans échéance", "tasks": nodate},
    ]

    # --- Bandeau "filtres actifs" (chips) ---
    current = {
        "status_f": status_f or "all",
        "urgent_f": urgent_f or "all",
        "important_f": important_f or "all",
        "q": (q or "").strip(),
        "sort": sort or "created_desc",
    }

    def is_active(key: str, val: str) -> bool:
        if key in ("status_f", "urgent_f", "important_f"):
            return val not in ("", None, "all")
        if key == "q":
            return bool(val)
        if key == "sort":
            return False
        return False

    def build_query(d: dict) -> str:
        keep = {}
        for k, v in d.items():
            if k in ("status_f", "urgent_f", "important_f"):
                if v and v != "all":
                    keep[k] = v
            elif k == "q":
                if v:
                    keep[k] = v
            elif k == "sort":
                if v:
                    keep[k] = v
        return "?" + urlencode(keep) if keep else ""

    def url_without(remove_key: str) -> str:
        copy = dict(current)
        if remove_key in ("status_f", "urgent_f", "important_f"):
            copy[remove_key] = "all"
        elif remove_key == "q":
            copy[remove_key] = ""
        return "/list" + build_query(copy)

    urls_clear = {
        "status_f": url_without("status_f"),
        "urgent_f": url_without("urgent_f"),
        "important_f": url_without("important_f"),
        "q": url_without("q"),
        "all": "/list",
    }

    has_filters = any(
        is_active(k, v)
        for k, v in current.items()
        if k in ("status_f", "urgent_f", "important_f", "q")
    )

    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "tasks": tasks,
            "due_sections": due_sections,
            "done_tasks": done_tasks,
            "status_f": current["status_f"],
            "urgent_f": current["urgent_f"],
            "important_f": current["important_f"],
            "q": current["q"],
            "sort": current["sort"],
            "urls_clear": urls_clear,
            "has_filters": has_filters,
            "total_count": total_count,
        },
    )


@app.get("/matrix", response_class=HTMLResponse)
def page_matrix(request: Request, db: Session = Depends(get_db)):
    # On ne montre que les tâches à faire dans la matrice
    tasks = crud.get_tasks(db, status="todo")

    q1 = []
    q2 = []
    q3 = []
    q4 = []

    for t in tasks:
        t.quadrant = compute_quadrant(t)
        t.due_status = compute_due_status(t.due_date)

        if t.quadrant == 1:
            q1.append(t)
        elif t.quadrant == 2:
            q2.append(t)
        elif t.quadrant == 3:
            q3.append(t)
        else:
            q4.append(t)

    return templates.TemplateResponse(
        "matrix.html",
        {
            "request": request,
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "q4": q4,
        },
    )


# Page de statistiques
@app.get("/stats", response_class=HTMLResponse)
def page_stats(request: Request, db: Session = Depends(get_db)):
    stats = crud.get_general_stats(db)
    total = stats["total"]
    done = stats["done"]
    todo = total - done
    completion_rate = round((done / total) * 100) if total else 0

    # Terminé récemment (7 derniers jours)
    now_utc = datetime.now(timezone.utc)
    seven_days_ago = now_utc - timedelta(days=7)
    done_last_7 = crud.get_completed_since_count(db, since=seven_days_ago)

    # Répartition Eisenhower
    eisenhower_all = crud.get_eisenhower_stats(db)
    eisenhower_todo = crud.get_eisenhower_stats(db, status="todo")

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "total": total,
            "done": done,
            "todo": todo,
            "completion_rate": completion_rate,
            "q_all": {
                "ii": eisenhower_all.get("q1", 0),
                "inu": eisenhower_all.get("q2", 0),
                "uni": eisenhower_all.get("q3", 0),
                "nn": eisenhower_all.get("q4", 0),
            },
            "q_todo": {
                "ii": eisenhower_todo.get("q1", 0),
                "inu": eisenhower_todo.get("q2", 0),
                "uni": eisenhower_todo.get("q3", 0),
                "nn": eisenhower_todo.get("q4", 0),
            },
            "done_last_7": done_last_7,
        },
    )


@app.post("/list/add")
def add_task_from_form(
    title: str = Form(...),
    urgent: bool = Form(False),
    important: bool = Form(False),
    due_date: str = Form(""),
    description: str = Form(""),
    db: Session = Depends(get_db),
):
    # Normaliser statut initial
    status_value = "todo"

    # Construire l'objet TaskCreate (schemas.TaskCreate)
    from . import schemas

    task_in = schemas.TaskCreate(
        title=title,
        description=description if description else None,
        urgent=urgent,
        important=important,
        due_date=due_date if due_date else None,
        status=status_value,
    )

    # Sauvegarder en base
    crud.create_task(db, task_in)

    # Rediriger vers /list pour rafraîchir l'affichage
    return RedirectResponse(url="/list", status_code=status.HTTP_303_SEE_OTHER)


# Marquer une tâche comme terminée
@app.post("/list/complete/{task_id}")
def complete_task_from_list(
    task_id: int,
    db: Session = Depends(get_db),
):
    from . import schemas

    task_in = schemas.TaskUpdate(status="done")
    crud.update_task(db, task_id, task_in)

    return RedirectResponse(url="/list", status_code=status.HTTP_303_SEE_OTHER)


# Rétablir une tâche terminée
@app.post("/list/reopen/{task_id}")
def reopen_task_from_list(
    task_id: int,
    db: Session = Depends(get_db),
):
    from . import schemas

    task_in = schemas.TaskUpdate(status="todo")
    crud.update_task(db, task_id, task_in)

    return RedirectResponse(url="/list", status_code=status.HTTP_303_SEE_OTHER)


# Modifier des tâches existantes
@app.get("/list/edit/{task_id}", response_class=HTMLResponse)
def edit_task_page(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    # Récupérer la tâche via la couche CRUD
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tâche introuvable")

    return templates.TemplateResponse(
        "edit_task.html",
        {
            "request": request,
            "task": task,
        },
    )


@app.post("/list/edit/{task_id}")
def edit_task_submit(
    task_id: int,
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(""),
    urgent: bool = Form(False),
    important: bool = Form(False),
    db: Session = Depends(get_db),
):
    from . import schemas

    task_in = schemas.TaskUpdate(
        title=title,
        description=description if description else None,
        due_date=due_date if due_date else None,
        urgent=urgent,
        important=important,
    )

    updated = crud.update_task(db, task_id, task_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Tâche introuvable")

    return RedirectResponse(url="/list", status_code=status.HTTP_303_SEE_OTHER)
