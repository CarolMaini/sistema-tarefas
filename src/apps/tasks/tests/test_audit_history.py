import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.audit.models import AuditEvent
from apps.tasks.models import Task
from apps.workspaces.models import Workspace


@pytest.fixture
def audit_history_context():
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="history-owner",
        email="history-owner@example.com",
        password="Strong-password-123!",
    )
    reader = user_model.objects.create_user(
        username="history-reader",
        email="history-reader@example.com",
        password="Strong-password-123!",
    )
    outsider = user_model.objects.create_user(
        username="history-outsider",
        email="history-outsider@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Histórico", owner=owner)
    workspace.memberships.create(user=reader, role="reader")
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa com histórico",
        created_by=owner,
    )
    event = AuditEvent.objects.create(
        actor=owner,
        workspace=workspace,
        task=task,
        action=AuditEvent.Action.TASK_CREATED,
    )
    return owner, reader, outsider, workspace, task, event


@pytest.mark.django_db
def test_workspace_owner_can_view_task_audit_history(client, audit_history_context):
    owner, _, _, workspace, task, event = audit_history_context
    client.force_login(owner)

    response = client.get(
        reverse("tasks:history", kwargs={"workspace_id": workspace.pk, "task_id": task.pk})
    )

    assert response.status_code == 200
    assert event.get_action_display().encode() in response.content
    assert owner.username.encode() in response.content


@pytest.mark.django_db
def test_workspace_reader_can_view_task_audit_history(client, audit_history_context):
    _, reader, _, workspace, task, event = audit_history_context
    client.force_login(reader)

    response = client.get(
        reverse("tasks:history", kwargs={"workspace_id": workspace.pk, "task_id": task.pk})
    )

    assert response.status_code == 200
    assert event.get_action_display().encode() in response.content


@pytest.mark.django_db
def test_non_member_cannot_view_task_audit_history(client, audit_history_context):
    _, _, outsider, workspace, task, _ = audit_history_context
    client.force_login(outsider)

    response = client.get(
        reverse("tasks:history", kwargs={"workspace_id": workspace.pk, "task_id": task.pk})
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_task_audit_history_cannot_cross_workspace_boundary(client, audit_history_context):
    owner, _, _, workspace, _, _ = audit_history_context
    other_workspace = Workspace.objects.create(name="Outro espaço", owner=owner)
    other_task = Task.objects.create(
        workspace=other_workspace,
        title="Tarefa de outro espaço",
        created_by=owner,
    )
    client.force_login(owner)

    response = client.get(
        reverse("tasks:history", kwargs={"workspace_id": workspace.pk, "task_id": other_task.pk})
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_task_audit_history_is_empty_when_no_events_exist(client):
    owner = get_user_model().objects.create_user(
        username="history-empty-owner",
        email="history-empty-owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Sem eventos", owner=owner)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa sem eventos",
        created_by=owner,
    )
    client.force_login(owner)

    response = client.get(
        reverse("tasks:history", kwargs={"workspace_id": workspace.pk, "task_id": task.pk})
    )

    assert response.status_code == 200
    assert b"Nenhuma atividade registrada." in response.content
