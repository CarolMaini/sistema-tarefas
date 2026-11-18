# Architecture

## Overview

The Organizador is a Django modular monolith. Its applications share one database and are separated by domain responsibility; the project does not use microservices or a separate SPA frontend.

## Django applications

| Application | Responsibility |
|---|---|
| `accounts` | Custom user model and authentication |
| `access` | Access-control support and authorization rules |
| `workspaces` | Shared workspaces, memberships, roles and workspace permissions |
| `tasks` | Tasks, attachments and task lifecycle |
| `scheduling` | Recurrence rules, dated occurrences, assignments and execution |
| `audit` | Audit events and history |
| `dashboard` | Dashboard views |
| `notifications` | Notification domain foundation; user-facing notification delivery remains a planned/incomplete capability |

## Runtime components

- Django Templates, HTML, Tailwind CSS and limited JavaScript provide the web interface.
- PostgreSQL is the production database; SQLite is used by the local test configuration.
- Celery, Redis and Celery Beat are included in the Compose environment for asynchronous processing and scheduled work.
- Gunicorn serves the production container; WhiteNoise serves collected static assets.
- Docker Compose orchestrates the local Django, PostgreSQL, Redis, Celery Worker and Celery Beat services.

## Quality workflow

GitHub Actions runs Ruff, Django checks, production configuration checks, migration consistency checks, pytest, a production Docker build and a container smoke test. The workflow currently tests Python 3.12.

For setup and operational requirements, see [deployment.md](deployment.md). Product requirements and planned capabilities are maintained in the root [spec.md](../spec.md).
