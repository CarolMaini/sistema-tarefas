# Authorization

The broader business authorization model is intentionally deferred to later phases.

For workspace membership additions, only the workspace owner or an active workspace manager may add an existing active account. The permission is checked on the server for every submission; collaborators and readers cannot add members. New memberships receive the collaborator role. Existing memberships, including inactive ones, are not duplicated or reactivated by this action.

Only the workspace owner or an active manager may remove a member or assign an occurrence to another person. Removing a member deactivates the membership and records an audit event; it does not delete the membership history. The workspace owner cannot be removed.

This feature-specific rule does not complete authorization for other business operations. The foundation still uses Django authentication and the custom user model; each future operation must define and enforce its own workspace permission boundary.
