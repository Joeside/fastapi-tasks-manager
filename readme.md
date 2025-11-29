FastAPI Tasks Manager

Un gestionnaire de tâches minimaliste, rapide, et organisé, basé sur FastAPI + SQLAlchemy + Jinja2

Description du projet

Ce projet est une application web complète permettant de :

Ajouter des tâches

Filtrer par urgence, importance, statut

Classer selon la matrice d’Eisenhower (Q1 à Q4)

Afficher les tâches en retard, aujourd’hui, bientôt, plus tard ou sans échéance

Marquer comme terminée / réouvrir une tâche

Visualiser les statistiques d’accomplissement

Utiliser une API REST complète (CRUD) sous /api/tasks

L’application est construite avec :

FastAPI (backend ultra rapide)

SQLAlchemy (ORM et SQLite)

Jinja2 (templates HTML)

CSS personnalisé

Architecture propre (models, schemas, CRUD, routers)

Ce projet fait partie du parcours d’apprentissage de Jonathan, et sert aussi de base à un futur portfolio professionnel.

Fonctionnalités principales
Gestion des tâches

Création de tâches

Date d’échéance optionnelle

Urgent / Important

Description

Statut : todo ou done

Affichage structuré

Page Liste (/list) avec filtres avancés

Page Matrice (/matrix) organisée par quadrants

Page Statistiques (/stats) :

taux de complétion

distribution Eisenhower

tâches terminées récemment

API REST complète

Disponible sous /api/tasks :

Méthode	Route	Description
GET	/api/tasks/	liste toutes les tâches
POST	/api/tasks/	crée une nouvelle tâche
GET	/api/tasks/{id}	obtient une tâche
PUT	/api/tasks/{id}	met à jour une tâche
DELETE	/api/tasks/{id}	supprime une tâche

Structure du projet
project-root/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── database.py
│   ├── routers/
│   │    └── tasks.py
│   ├── templates/
│   │    ├── list.html
│   │    ├── matrix.html
│   │    └── stats.html
│   ├── static/
│   │    └── app.css
│   └── data/
│        └── app.db
│
├── README.md
└── .gitignore

Installation et exécution locale
1️- Cloner le projet
git clone https://github.com/Joeside/fastapi-tasks-manager.git
cd fastapi-tasks-manager

2️- Créer un environnement virtuel
python -m venv .venv
.\.venv\Scripts\activate

3️- Installer les dépendances
pip install -r requirements.txt

4️- Lancer le serveur
uvicorn app.main:app --reload

5️- Ouvrir dans le navigateur

Application : http://127.0.0.1:8000/list

API Swagger : http://127.0.0.1:8000/docs

Prochaines fonctionnalités prévues

Page modifier une tâche

Suppression depuis l’interface

Exportation CSV / JSON

Comptes utilisateurs

Déploiement cloud (Render ou Railway)

Contact

Projet réalisé par Jonathan
Contact professionnel : à compléter

Si tu trouves ce projet utile, laisse une étoile sur GitHub !
