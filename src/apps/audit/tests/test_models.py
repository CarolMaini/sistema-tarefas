import pytest
from django.contrib.auth import get_user_model

from apps.audit.models import AuditEvent
from apps.workspaces.models import Workspace


@pytest.mark.django_db
def test_audit_event_records_workspace_member_addition():
    user_model = get_user_model()
    actor = user_model.objects.create_user(
        username="workspace-manager",
        email="manager@example.com",
        password="Strong-password-123!",
    )
    target = user_model.objects.create_user(
        username="new-member",
        email="member@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Equipe", owner=actor)

    event = AuditEvent.objects.create(
        actor=actor,
        workspace=workspace,
        target_user=target,
        action=AuditEvent.Action.WORKSPACE_MEMBER_ADDED,
    )

    assert event.actor == actor
    assert event.workspace == workspace
    assert event.target_user == target
    assert event.action == AuditEvent.Action.WORKSPACE_MEMBER_ADDED
    assert event.created_at is not None