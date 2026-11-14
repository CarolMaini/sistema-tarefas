# Quickstart: Membros e Navegação do Workspace

## Prerequisites

- Project dependencies installed in `.venv` and local settings configured.
- PostgreSQL available as configured for the local environment.
- A browser and test accounts: workspace owner, active manager, collaborator, reader, active unassociated user, inactive user, and an account with an existing inactive membership.

## Automated Validation

Run from the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest src\apps\workspaces\tests src\apps\audit\tests
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check src\apps\workspaces src\apps\audit
.\.venv\Scripts\python.exe .\src\manage.py check --settings=setup.settings.local
.\.venv\Scripts\python.exe .\src\manage.py migrate --check --settings=setup.settings.local
```

Expected results: focused and full tests pass; Ruff and Django checks report no errors; migrations are current after the audit-event migration is applied.

## Membership Acceptance Checks

1. Sign in as the owner or an active manager and open a workspace detail.
2. Submit the email of an active account with no membership. Confirm one collaborator membership and one audit event, then confirm the member appears in the list.
3. Submit an unknown email, an inactive account, an existing active member, the workspace owner, and an account with an inactive membership. Confirm no duplicate or reactivation and an appropriate message for each case.
4. Repeat the add-member POST as a collaborator, reader, and anonymous visitor. Confirm no membership or audit event is created.
5. Submit two concurrent attempts for the same account. Confirm the unique membership constraint leaves one membership and only the successful addition is audited.

## Navigation and Visual Acceptance Checks

1. Visit each of the nine authenticated screens through internal navigation and directly by URL. Verify the icon returns to same-origin history or the contextual fallback in [the UI contract](contracts/workspace-ui.md).
2. Visit a screen after navigating from another site; activate the icon and verify navigation stays inside the application.
3. Use keyboard navigation to focus the icon and buttons. Verify the icon has an accessible name, a tooltip, and a visible focus state.
4. Inspect primary, secondary, and destructive controls on desktop and mobile at normal, hover, focus, and disabled states. Verify the text and icons remain readable and meet the specified contrast targets.

## Design References

- [Data model](data-model.md)
- [UI contract](contracts/workspace-ui.md)
- [Research decisions](research.md)