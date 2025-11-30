![CI](https://github.com/Joeside/fastapi-tasks-manager/actions/workflows/ci.yml/badge.svg)

# FastAPI Tasks Manager

Un gestionnaire de tâches minimaliste, rapide, et organisé, basé sur **FastAPI + SQLAlchemy + Jinja2**

## 📖 Description du projet

Application web complète de gestion de tâches avec :
- ✅ Création et gestion de tâches
- 📊 Classification selon la **matrice d'Eisenhower** (Q1 à Q4)
- 🔄 **Tâches récurrentes** (quotidiennes, hebdomadaires, mensuelles, annuelles)
- ✨ **Sous-tâches** pour décomposer les grandes tâches
- 📅 Gestion des échéances avec alertes visuelles
- 🎯 Filtres avancés par urgence, importance, statut
- 🗑️ Suppression de tâches depuis toutes les vues
- 📈 Statistiques et visualisation de la productivité
- 🚀 API REST complète

### Stack technique
- **Backend** : FastAPI (ultra rapide et moderne)
- **Base de données** : SQLAlchemy + SQLite (+ Alembic pour les migrations)
- **Frontend** : Jinja2 templates + Tailwind CSS + HTML5 Drag & Drop API
- **Architecture** : Clean architecture (models, schemas, CRUD, routers)
- **Tests** : pytest avec 9 tests passants

Ce projet fait partie du parcours d'apprentissage de Jonathan, et sert de base à un futur portfolio professionnel.

---

## ✨ Fonctionnalités principales

### 🎯 Gestion des tâches
- Création de tâches avec titre, description, échéance
- Classification **urgent / important** (matrice d'Eisenhower)
- Statut : **todo** ou **done**
- **Sous-tâches** : décomposez vos tâches en étapes plus petites
  - Ajout/modification/suppression dans la page d'édition
  - Cocher/décocher pour suivre la progression
  - Réorganisation par drag & drop
- **Récurrence** : création automatique de la prochaine occurrence
  - Patterns : quotidien, hebdomadaire, mensuel, annuel
  - Date de fin de récurrence optionnelle
  - Génération automatique lors du marquage comme "terminée"
- **Suppression** : bouton 🗑️ dans toutes les vues avec confirmation

### 📋 Affichage structuré
- **Page Liste** (`/list`)
  - Filtres avancés (urgent, important, statut, recherche)
  - Sections par échéance (en retard, aujourd'hui, cette semaine, etc.)
  - Drag & drop pour réorganiser
  - Badges visuels pour les priorités et échéances
- **Page Matrice** (`/matrix`)
  - Quadrants Eisenhower interactifs
  - **Drag & drop amélioré** : déposez n'importe où dans un quadrant
  - Zone de drop permissive avec feedback visuel
  - Support des quadrants vides
- **Page Statistiques** (`/stats`)
  - Taux de complétion
  - Distribution par quadrant
  - Graphiques de productivité
- **Page Édition** (`/list/edit/{id}`)
  - Modification complète d'une tâche
  - Gestion des sous-tâches
  - Configuration de la récurrence

### 🔧 API REST complète

#### Endpoints Tâches (`/api/tasks`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/tasks/` | Liste toutes les tâches |
| POST | `/api/tasks/` | Crée une nouvelle tâche |
| GET | `/api/tasks/{id}` | Obtient une tâche |
| PUT | `/api/tasks/{id}` | Met à jour une tâche |
| DELETE | `/api/tasks/{id}` | Supprime une tâche |
| POST | `/api/tasks/reorder` | Réorganise les positions |
| PATCH | `/api/tasks/{id}/position` | Met à jour la position |
| PATCH | `/api/tasks/{id}/quadrant` | Change le quadrant |

#### Endpoints Sous-tâches (`/api/tasks/{task_id}/subtasks/`)

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/` | Liste les sous-tâches |
| POST | `/` | Crée une sous-tâche |
| GET | `/{subtask_id}` | Obtient une sous-tâche |
| PUT | `/{subtask_id}` | Met à jour une sous-tâche |
| DELETE | `/{subtask_id}` | Supprime une sous-tâche |
| POST | `/reorder` | Réorganise l'ordre |

---

## 📁 Structure du projet

```
project-root/
│
├── alembic/                    # Migrations de base de données
│   ├── versions/
│   └── env.py
│
├── app/
│   ├── main.py                # Point d'entrée FastAPI
│   ├── models.py              # Modèles SQLAlchemy
│   ├── schemas.py             # Schémas Pydantic
│   ├── crud.py                # Logique métier
│   ├── database.py            # Configuration DB
│   │
│   ├── routers/               # Endpoints API
│   │   ├── tasks.py
│   │   └── subtasks.py
│   │
│   ├── templates/             # Templates Jinja2
│   │   ├── base.html
│   │   ├── list.html
│   │   ├── edit_task.html
│   │   ├── matrix.html
│   │   └── stats.html
│   │
│   ├── static/
│   │   └── app.css           # Styles personnalisés
│   │
│   └── data/
│       └── app.db            # Base de données SQLite
│
├── tests/                     # Tests unitaires
│   ├── test_main.py
│   ├── test_crud.py
│   ├── test_subtasks.py
│   └── test_recurrence.py
│
├── CHANGELOG.md              # Historique des versions
├── README.md
├── requirements.txt
├── alembic.ini
└── .gitignore
```

---

## 🚀 Installation et exécution locale

### 1️⃣ Cloner le projet
```bash
git clone https://github.com/Joeside/fastapi-tasks-manager.git
cd fastapi-tasks-manager
```

### 2️⃣ Créer un environnement virtuel
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3️⃣ Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4️⃣ Appliquer les migrations
```bash
alembic upgrade head
```

### 5️⃣ Lancer le serveur
```bash
uvicorn app.main:app --reload
```

### 6️⃣ Ouvrir dans le navigateur
- **Application** : http://127.0.0.1:8000/list
- **API Swagger** : http://127.0.0.1:8000/docs
- **Matrice d'Eisenhower** : http://127.0.0.1:8000/matrix
- **Statistiques** : http://127.0.0.1:8000/stats

---

## 🧪 Tests

Lancer les tests :
```bash
pytest
```

Avec couverture :
```bash
pytest --cov=app tests/
```

---

## 📝 Changelog

Voir [CHANGELOG.md](./CHANGELOG.md) pour l'historique détaillé des versions.

### Version actuelle : v0.5 (2025-11-30)
- ✨ Sous-tâches avec API complète
- 🔄 Tâches récurrentes (quotidien, hebdomadaire, mensuel, annuel)
- 🗑️ Suppression de tâches depuis toutes les vues
- 🎯 Drag & drop amélioré dans la matrice (zone permissive)

---

## 🗺️ Roadmap

Voir [Roadmap.txt](./Roadmap.txt) pour la feuille de route complète.

### Prochaines fonctionnalités prévues
- [ ] Recherche avancée et filtres sauvegardés
- [ ] Notifications par email pour les échéances
- [ ] Thème sombre/clair
- [ ] Exportation CSV / JSON
- [ ] Authentification multi-utilisateurs
- [ ] Déploiement cloud (Render ou Railway)
- [ ] Progressive Web App (PWA)

---

## 📧 Contact

**Projet réalisé par Jonathan**
Portfolio professionnel en construction

Si tu trouves ce projet utile, laisse une ⭐ sur GitHub !

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.
