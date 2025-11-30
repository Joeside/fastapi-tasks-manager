# Changelog

Toutes les modifications importantes de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [v0.5] - 2025-11-30

### Ajouté
- **Sous-tâches** : Possibilité d'ajouter des sous-tâches à chaque tâche
  - Interface dans la page d'édition pour gérer les sous-tâches
  - API REST complète (`/api/tasks/{task_id}/subtasks/`)
  - Création, modification, suppression et réorganisation
  - Cocher/décocher pour marquer comme complétées
- **Récurrence des tâches** : Création automatique de la prochaine occurrence
  - Patterns disponibles : quotidien, hebdomadaire, mensuel, annuel
  - Date de fin de récurrence optionnelle
  - Génération automatique lors du marquage comme "terminée"
- **Suppression de tâches** : Bouton 🗑️ dans les vues Liste et Matrice
  - Confirmation avant suppression
  - Suppression via API REST (`DELETE /api/tasks/{id}`)
- **Amélioration drag & drop (Matrice)** :
  - Remplacement de SortableJS par l'API HTML5 Drag & Drop native
  - Possibilité de déposer une tâche n'importe où dans un quadrant
  - Zone de drop beaucoup plus permissive
  - Effet visuel lors du survol d'un quadrant
  - Support des quadrants vides avec placeholder

### Modifié
- Migration de la base de données pour ajouter les champs de récurrence
- Migration pour la table des sous-tâches avec relation FK
- Interface d'édition des tâches avec sections pour sous-tâches et récurrence
- Amélioration du style des zones de drop dans la matrice

### Technique
- Alembic migrations : `dbb6eede6d13` (subtasks + recurrence)
- Tests : 9 tests passants (subtasks API, recurrence logic, reorder)
- Backend : FastAPI + SQLAlchemy + Pydantic V2
- Frontend : Jinja2 + Tailwind CSS + HTML5 Drag & Drop API

## [v0.4] - 2025-11-29

### Ajouté
- Position des tâches dans les quadrants de la matrice d'Eisenhower
- API pour réorganiser les tâches (`/api/tasks/reorder`)
- Drag & drop fonctionnel dans la vue Matrice avec SortableJS

### Modifié
- Amélioration de l'affichage des badges d'échéance
- Refactoring du calcul du statut d'échéance

## [v0.3] - 2025-11-28

### Ajouté
- Filtres avancés dans la page Liste (urgent, important, statut, recherche)
- Badges visuels pour les échéances (retard, aujourd'hui, bientôt)
- Sections par échéance dans la liste des tâches

### Modifié
- Amélioration du design avec CSS personnalisé
- Harmonisation des couleurs et badges

## [v0.2] - 2025-11-27

### Ajouté
- Page Statistiques (`/stats`) avec graphiques
- Taux de complétion et distribution des tâches
- API REST complète sous `/api/tasks`

## [v0.1] - 2025-11-26

### Ajouté
- Version initiale MVP
- CRUD complet pour les tâches
- Pages : Liste, Matrice d'Eisenhower, Statistiques
- Base de données SQLite
- Modèle Task avec champs : titre, description, urgent, important, quadrant, échéance, statut
- Interface web avec Jinja2 et Tailwind CSS
