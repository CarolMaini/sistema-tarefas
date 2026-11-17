# Authorization

All workspace operations require an authenticated user and enforce access on the server. An active workspace membership is required unless the user is the workspace owner. Inactive workspaces and inactive memberships do not grant access.

## Workspace roles

| Operation | Owner | Manager | Collaborator | Reader |
|---|---:|---:|---:|---:|
| View workspace and its tasks/occurrences | Yes | Yes | Yes | Yes |
| Add an existing active account as a member | Yes | Yes | No | No |
| Remove/deactivate a member | Yes | Yes | No | No |
| Create tasks and recurrence rules | Yes | Yes | Yes | No |
| Assign an occurrence to an eligible workspace member | Yes | Yes | Yes | No |
| Register execution for own assignment | Yes, if assigned | Yes, if assigned | Yes, if assigned | Yes, if assigned |
| Complete own assignment after registering execution | Yes, if assigned | Yes, if assigned | Yes, if assigned | Yes, if assigned |

The role checks are implemented by `Workspace.can_view()`, `Workspace.can_manage_space()` and `Workspace.can_create_tasks()`. The owner has the same task-creation and assignment capabilities as a manager, while retaining ownership-specific controls.

## Membership management

Only the workspace owner or an active manager may add an existing active account or deactivate a member. New memberships receive the collaborator role. Existing memberships, including inactive ones, are not duplicated or silently reactivated by the add-member action. Deactivation preserves membership history and records an audit event; the workspace owner cannot be removed.

## Occurrence assignment and execution

The owner, an active manager or an active collaborator may assign an occurrence to the workspace owner or an active member. Readers and inactive members cannot assign occurrences. The server validates both the actor's permission and the assignee's eligibility; HTML form options are not a security boundary.

A user may register execution only for their own pending assignment. An assignment can be completed only by its assignee and only after at least one execution record exists. Completed or cancelled assignments cannot be completed again.

This document describes the current implemented workspace authorization rules. Any new operation must define and enforce its own workspace permission boundary and add regression tests for allowed and denied roles.
