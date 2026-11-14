# Implementation Plan: Membros e Navegação do Workspace

**Branch**: `002-workspace-members-navigation` | **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)

**Input**: Executar o planejamento de `002-workspace-members-navigation`.

## Summary

Adicionar uma conta ativa existente a um workspace pelo e-mail, autorizando somente proprietária ou gestora e atribuindo o papel padrão de colaboradora. Reutilizar `WorkspaceMembership` e sua restrição de unicidade; registrar a inclusão no app de auditoria, conforme a Constitution. Centralizar o controle de retorno e os estilos semânticos de botões no layout e na folha de estilos compartilhados, com fallback interno contextual e estados acessíveis.

## Technical Context

**Language/Version**: Python 3.12 (`>=3.12,<3.13`)

**Primary Dependencies**: Django 6.1.2, Django Templates, Tailwind CSS browser build; no new dependency planned

**Storage**: PostgreSQL; existing `Workspace`, `WorkspaceMembership`, and custom `accounts.User`; one new audit event model and migration

**Testing**: pytest, pytest-django, Ruff; Django test client for authorization and form flows, plus manual browser checks for navigation and visual states

**Target Platform**: Responsive web application in supported desktop and mobile browsers

**Project Type**: Modular Django web application

**Performance Goals**: No new throughput target; account lookup and membership creation are interactive single-request operations

**Constraints**: Validate permissions and eligibility on the server; preserve CSRF protection and membership uniqueness; never use an external referrer as a return destination; audit membership changes without sensitive data; maintain at least 4.5:1 normal-text and 3:1 large-text contrast

**Scale/Scope**: Workspace member detail flow, shared authenticated layout, nine authenticated page templates, and one focused audit event

## Constitution Check

*GATE: Evaluated before Phase 0 research and re-checked after Phase 1 design.*

| Principle / gate | Before design | After design |
|---|---|---|
| Modular architecture and simplicity | PASS: extend `apps.workspaces`, shared templates and existing stylesheet; no new dependency | PASS: new form and audit event stay in their owning Django apps |
| Business integrity and maintainability | PASS: reuse membership model and unique constraint; use a transaction for membership plus audit | PASS: no duplicate membership model or unrelated business features |
| Security and least privilege | PASS: authenticate, authorize owner/manager on the server, validate active account, retain CSRF protection | PASS: internal-only navigation fallback and bounded audit data are documented |
| Audit and data protection | PASS WITH DESIGN ACTION: constitution requires important actions to be audited; current `apps.audit` has no event model | PASS: add one append-only membership-added event, written atomically and without secrets or sensitive payloads |
| Quality gates | PASS: add focused pytest-django coverage and run Ruff and Django checks | PASS: quickstart lists focused and full checks plus manual UI validation |

The authorization documentation describes the broader business authorization model as deferred. This feature implements only the permission boundary required for adding workspace members; it does not claim to complete global authorization for other operations.

## Project Structure

### Documentation (this feature)

```text
specs/002-workspace-members-navigation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── workspace-ui.md
└── tasks.md              # Created by /speckit-tasks
```

### Source Code (repository root)
```text
src/
├── setup/settings/base.py            # Register the audit app
├── apps/
│   ├── audit/
│   │   ├── models.py                 # New append-only audit event
│   │   ├── migrations/               # New audit event migration
│   │   └── tests/                    # New audit event tests
│   └── workspaces/
│       ├── forms.py                  # New existing-account lookup form
│       ├── urls.py                   # Member-add route
│       ├── views.py                  # Authorized member-add flow
│       └── tests/
│           └── test_views.py         # Membership and permission scenarios
├── static/css/auth.css               # Shared semantic colors and button states
└── templates/
  ├── base.html                     # Shared back control and authenticated shell
  ├── workspaces/workspace_detail.html # Member-add form and updated member list
  ├── dashboard/dashboard.html
  ├── tasks/{task_list,task_form}.html
  ├── workspaces/{workspace_list,workspace_form}.html
  └── scheduling/{calendar,schedule_form,occurrence_detail}.html
```

**Structure Decision**: Use the existing modular Django structure. Keep membership validation and its view in `apps.workspaces`; keep the auditable event in `apps.audit`; render the form and shared navigation in the existing Django templates. The nine authenticated templates inherit `base.html`; login and signup remain outside the authenticated navigation treatment. Reuse the loaded `auth.css` palette and do not add a frontend package.

## Complexity Tracking

No constitution violations remain after the documented audit event design. The single audit model is required by the existing audit principle and is limited to this membership action.
