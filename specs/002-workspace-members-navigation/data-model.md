# Data Model: Membros e Navegação do Workspace

## Existing Entities

### User (`accounts.User`)

- **Purpose**: Represents an account that can be associated with a workspace.
- **Relevant fields**: `id`; unique `email`; inherited `is_active`.
- **Relationships**: Has workspace memberships and may own workspaces.
- **Validation**: Only an active account may be added by this flow. Resolve the submitted email after trimming surrounding whitespace and without case sensitivity. If lookup is ambiguous, do not associate either account.
- **Changes**: No schema change.

### Workspace

- **Purpose**: Owns workspace membership and defines its owner and managers.
- **Relevant fields**: `id`; `owner_id`; active state.
- **Relationships**: Has memberships and tasks; belongs to an owner.
- **Validation**: The add-member operation requires the owner or an active membership with role `MANAGER`.
- **Changes**: No schema change.

### WorkspaceMembership

- **Purpose**: Represents a user's role and active state within a workspace.
- **Relevant fields**: `workspace_id`; `user_id`; `role`; `is_active`; `joined_at`.
- **Relationships**: Belongs to one workspace and one user.
- **Validation rules**:
  - The workspace/user pair is unique, including inactive memberships.
  - A new membership uses role `COLLABORATOR` and `is_active=True`.
  - A user who already has any membership, including an inactive one, is not added again or reactivated by this feature.
  - The workspace owner is not given a duplicate membership by this flow.
- **Changes**: No schema change; reuse the existing database uniqueness constraint.

## New Entity

### AuditEvent (`apps.audit`)

- **Purpose**: Retains a minimal record of successful changes to workspace access, including additions and removals.
- **Fields**:
  - `id`: generated primary key.
  - `actor_id`: authenticated user who added the member.
  - `workspace_id`: workspace receiving the membership.
  - `target_user_id`: account that became a member.
  - `action`: stable event type identifying a workspace-member addition or removal.
  - `created_at`: event timestamp.
- **Relationships**: References the actor, workspace, and target account.
- **Validation rules**:
  - Create an event only after an authorized membership addition or removal.
  - Persist the membership change and event in one database transaction; failure to record the event must roll back the change.
  - Treat events as append-only through the application flow.
  - Do not store submitted passwords, tokens, raw form payloads, or unrelated personal data.
- **Migration**: Add a table through the `apps.audit` migration sequence. No data migration is needed for existing memberships.

## State and Transaction Flow

1. Authenticate the requester and confirm workspace-management permission for member changes or manual occurrence assignments.
2. Resolve one active account from the submitted selector, or the active membership targeted for removal.
3. Reject the workspace owner or any account with an existing membership when adding; never remove the workspace owner.
4. In one transaction, create an active `COLLABORATOR` membership or deactivate the selected membership and write the corresponding audit event.
5. On any validation or database conflict, preserve existing data and return an informative result; do not emit a success audit event.

Navigation history and button presentation are view state only and introduce no persisted entities.