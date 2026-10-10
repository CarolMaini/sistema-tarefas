# Copilot instructions for Organizador de Tarefas

## Project scope
This repository is in the foundation phase of the Organizador de Tarefas project. Implement only the work defined by the Fase 1 scope in `spec.md` and avoid business modules from later phases.

## Core constraints
- Keep the architecture aligned with the specification.
- Use the custom user model `accounts.User` via `AUTH_USER_MODEL`.
- Keep shared settings in `src/setup/settings/base.py`.
- Keep development and production settings separate in `local.py` and `prod.py`.
- Do not commit secrets or production values in the repository.
- Use PostgreSQL as the primary data store, Redis as the Celery broker, and Docker Compose for local orchestration.
- Prefer explicit, maintainable code over unnecessary abstractions.

## Execution guidance
1. Build the base stack before business features.
2. Verify migrations, Django startup, and test execution after changes.
3. Preserve the folder structure defined by the specification.
4. Add only files with a clear purpose.
5. Keep all new documentation brief and operational.

## Quality gates
- Run pytest for focused validation.
- Run Ruff before concluding a task.
- Verify Django configuration with `python src/manage.py check`.
- Prefer idempotent and testable implementations.
