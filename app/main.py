from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone, date
from typing import Optional
from urllib.parse import urlencode

from .database import Base, engine, get_db
from .models import Task
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


def compute_due_status(due_date_str: Optional[str]) -> str:
    """
    Retourne l'un de :
    - "none"      : pas d'échéance
    - "overdue"   : en retard
    - "today"     : aujourd'hui
    - "soon"      : dans les 7 prochains jours
    - "later"     : plus tard
    """
    if not due_date_str:
        return "none"
    try:
        d = datetime.strptime(due_date_str, "%Y-%m-%d").date()
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
    tasks = crud.get_tasks(db)
    total_count = len(tasks)

    # --- Filtres ---
    def yesno(val: Optional[str]):
        if val is None or val == "" or val == "all":
            return None
        return True if val == "yes" else False

    status_val = status_f if status_f in {"todo", "done"} else None
    urgent_val = yesno(urgent_f)
    important_val = yesno(important_f)

    if status_val:
        tasks = [t for t in tasks if t.status == status_val]
    if urgent_val is not None:
        tasks = [t for t in tasks if bool(t.urgent) == urgent_val]
    if important_val is not None:
        tasks = [t for t in tasks if bool(t.important) == important_val]
    if q and q.strip():
        needle = q.strip().lower()
        tasks = [
            t
            for t in tasks
            if needle in (t.title or "").lower()
            or needle in (t.description or "").lower()
        ]

    # --- Tri (par défaut : création décroissante) ---
    sort_key = sort or "created_desc"

    def parse_due(date_str: Optional[str]):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            return None

    if sort_key == "due_asc":
        tasks = sorted(
            tasks,
            key=lambda t: (
                parse_due(t.due_date) is None,
                parse_due(t.due_date),
                t.id,
            ),
        )
    elif sort_key == "due_desc":
        tasks = sorted(
            tasks,
            key=lambda t: (
                parse_due(t.due_date) is None,
                parse_due(t.due_date) or date.min,
            ),
            reverse=True,
        )
    else:  # "created_desc"
        tasks = sorted(tasks, key=lambda t: t.created_at, reverse=True)

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
    tasks = crud.get_tasks(db)

    q1 = []
    q2 = []
    q3 = []
    q4 = []

    for t in tasks:
        if t.status == "done":
            # On ne montre pas les tâches terminées dans la matrice
            continue
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
    all_tasks = crud.get_tasks(db)
    total = len(all_tasks)
    done = sum(1 for t in all_tasks if t.status == "done")
    todo = total - done
    completion_rate = round((done / total) * 100) if total else 0

    # Répartition Eisenhower (toutes tâches)
    q_urgent_important_all = sum(1 for t in all_tasks if t.urgent and t.important)
    q_important_not_urgent_all = sum(
        1 for t in all_tasks if (not t.urgent) and t.important
    )
    q_urgent_not_important_all = sum(
        1 for t in all_tasks if t.urgent and (not t.important)
    )
    q_neither_all = sum(1 for t in all_tasks if (not t.urgent) and (not t.important))

    # Répartition Eisenhower (seulement à faire)
    todos = [t for t in all_tasks if t.status != "done"]
    q_urgent_important_todo = sum(1 for t in todos if t.urgent and t.important)
    q_important_not_urgent_todo = sum(
        1 for t in todos if (not t.urgent) and t.important
    )
    q_urgent_not_important_todo = sum(
        1 for t in todos if t.urgent and (not t.important)
    )
    q_neither_todo = sum(1 for t in todos if (not t.urgent) and (not t.important))

    # Terminé récemment (7 derniers jours)
    now_utc = datetime.now(timezone.utc)
    seven_days_ago = now_utc - timedelta(days=7)
    done_last_7 = 0
    for t in all_tasks:
        if t.status == "done" and t.completed_at:
            comp = t.completed_at
            if comp.tzinfo is None:
                comp = comp.replace(tzinfo=timezone.utc)
            if comp >= seven_days_ago:
                done_last_7 += 1

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "total": total,
            "done": done,
            "todo": todo,
            "completion_rate": completion_rate,
            "q_all": {
                "ii": q_urgent_important_all,
                "inu": q_important_not_urgent_all,
                "uni": q_urgent_not_important_all,
                "nn": q_neither_all,
            },
            "q_todo": {
                "ii": q_urgent_important_todo,
                "inu": q_important_not_urgent_todo,
                "uni": q_urgent_not_important_todo,
                "nn": q_neither_todo,
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
    updated = crud.update_task(db, task_id, task_in)

    return RedirectResponse(url="/list", status_code=status.HTTP_303_SEE_OTHER)


# Rétablir une tâche terminée
@app.post("/list/reopen/{task_id}")
def reopen_task_from_list(
    task_id: int,
    db: Session = Depends(get_db),
):
    from . import schemas

    task_in = schemas.TaskUpdate(status="todo")
    updated = crud.update_task(db, task_id, task_in)

    return RedirectResponse(url="/list", status_code=status.HTTP_303_SEE_OTHER)
