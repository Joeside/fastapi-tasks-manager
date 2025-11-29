# Contributing

Thanks for wanting to contribute! A few quick guidelines to get started.

- Run the linter and tests locally before opening a PR:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
pip install ruff pytest
python -m ruff check .
python -m pytest -q
```

- Follow the existing code style (ruff rules in `.ruff.toml`).
- For DB schema changes, prefer Alembic migrations (scaffolded in `alembic/`).

If you open a PR I will run the CI (lint + tests) automatically.
