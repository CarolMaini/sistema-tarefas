# UI Contract: Workspace Membership and Authenticated Navigation

## Add Workspace Member

- **Entry point**: Member-add form on the workspace detail screen.
- **Submission**: Authenticated, CSRF-protected `POST` to `workspaces/<uuid:pk>/members/add/` (`workspaces:member-add`).
- **Input**: Required identifier selected from the list of active accounts that are not the workspace owner and have no membership in the workspace.
- **Permission**: Workspace owner or active workspace manager only. Enforce permission on the server for every submission; an unavailable workspace or unauthorized request must not change membership.
- **Success**: Create one active `COLLABORATOR` membership and one corresponding audit event; redirect to the workspace detail with a success message and the new member visible.
- **Unavailable, inactive, or forged account choice**: Create no membership; return to workspace detail with a clear error message.
- **Existing membership, including inactive membership, or workspace owner**: Preserve existing state, create no duplicate and no success audit event; return an informational message.
- **Concurrent uniqueness conflict**: Create no additional membership; return a safe informational/error message without exposing unrelated account details.
- **Error behavior**: Do not reveal whether an account belongs to another workspace. Do not include sensitive data in messages or audit records.

## Remove Workspace Member

- **Entry point**: Remove action beside active members on the workspace detail screen; render only for the owner or an active workspace manager.
- **Submission**: Authenticated, CSRF-protected `POST` to `workspaces/<uuid:pk>/members/<int:membership_id>/remove/` (`workspaces:member-remove`).
- **Permission**: Enforce owner/active-manager permission on the server for every submission. Collaborators and readers cannot remove memberships.
- **Target restrictions**: Only active memberships in the specified workspace can be removed. The workspace owner cannot be removed.
- **Success**: Deactivate the membership, preserve its history, write a removal audit event in the same transaction, and omit it from the active member list.

## Assign Occurrence

- **Permission**: The workspace owner, an active workspace manager, or an active collaborator can manually assign an occurrence to the workspace owner or another active workspace member. Readers and inactive members cannot assign occurrence responsibilities.
- **Enforcement**: Hide the assignment form from readers and inactive members, and reject their direct POST attempts server-side without creating an assignment. Validate the actor's permission and the assignee's active membership on the server; form options are not a security boundary.

## Back Control

- **Appearance**: Icon-only control, no visible text label; accessible name and hover tooltip identify it as “Voltar”. Provide a visible keyboard-focus indicator and an adequate hit target.
- **Placement and coverage**: Shared authenticated shell, present on all nine authenticated screens: dashboard; workspace list, detail, and form; task list and form; calendar, schedule form, and occurrence detail. Public login and signup screens are excluded.
- **Behavior**: Use browser back only when the previous document is from the same application origin. Otherwise navigate to the internal fallback below. Never redirect to an external referrer.

| Current screen | Internal fallback |
|---|---|
| Dashboard | Workspace list |
| Workspace list | Dashboard |
| Workspace form | Workspace list |
| Workspace detail | Workspace list |
| Task list | Current workspace detail |
| Task form | Current workspace task list |
| Calendar | Current workspace detail |
| Schedule form | Current workspace calendar |
| Occurrence detail | Current workspace calendar |

## Button Visual Contract

- Apply the shared semantic styles to controls presented as buttons on authenticated screens, including button-like links.
- Primary actions use the established forest color family; secondary actions use a light surface with readable foreground and border; destructive actions use the established error color family. Coordinate colors with the action label and surrounding text.
- Hover, keyboard focus, and disabled states are visibly distinct; focus must not depend on color alone. Preserve readable text and icon contrast in every state.
- Communicate action intent through its label or icon as well as color.
- Meet the specification contrast targets: at least 4.5:1 for normal-size text and 3:1 for large text.
- Keep public authentication screens' existing visual treatment unchanged unless a shared token change is required to maintain the same existing appearance.
