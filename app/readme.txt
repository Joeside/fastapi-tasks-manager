App Gestion de temps
Chemin du dossier en local:
C:\Users\"Laptop Jonathan"\OneDrive\apps\"Saas Gestion du temps"

Lancer .venv:
.venv\Scripts\activate

Pour lancer le server:
uvicorn app.main:app --reload

Pour accéder au site:

Liste des tâches
http://localhost:8000/list

Matrice Eisenhower
http://localhost:8000/matrix

API JSON (toutes les tâches)
http://localhost:8000/api/tasks

