import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.audit.models import AuditEvent
from apps.tasks.models import Task
from apps.workspaces.models import Workspace, WorkspaceMembership


def create_user(username):
    return get_user_model().objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="Strong-password-123!",
    )


def history_url(workspace, task):
    return reverse(
        "tasks:history",
        kwargs={"workspace_id": workspace.pk, "task_id": task.pk},
    )


@pytest.mark.django_db
def test_task_history_requires_login(client):
    owner = create_user("history-login-owner")
    workspace = Workspace.objects.create(name="Histórico privado", owner=owner)
    task = Task.objects.create(workspace=workspace, title="Tarefa privada", created_by=owner)

    response = client.get(history_url(workspace, task))

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


@pytest.mark.django_db
def test_owner_can_view_task_history_and_events_are_scoped_to_task(client):
    owner = create_user("history-owner")
    workspace = Workspace.objects.create(name="Histórico da equipe", owner=owner)
    task = Task.objects.create(workspace=workspace, title="Tarefa auditada", created_by=owner)
    another_task = Task.objects.create(
        workspace=workspace,
        title="Outra tarefa",
        created_by=owner,
    )
    visible_event = AuditEvent.objects.create(
        actor=owner,
        workspace=workspace,
        task=task,
        action=AuditEvent.Action.TASK_CREATED,
    )
    hidden_event = AuditEvent.objects.create(
        actor=owner,
        workspace=workspace,
        task=another_task,
        action=AuditEvent.Action.TASK_UPDATED,
    )
    client.force_login(owner)

    response = client.get(history_url(workspace, task))

    assert response.status_code == 200
    assert list(response.context["events"]) == [visible_event]
    assert visible_event.get_action_display().encode() in response.content
    assert hidden_event.get_action_display().encode() not in response.content


@pytest.mark.django_db
def test_active_workspace_member_can_view_task_history(client):
    owner = create_user("history-member-owner")
    member = create_user("history-member")
    workspace = Workspace.objects.create(name="Histórico compartilhado", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=member,
        role=WorkspaceMembership.Role.READER,
    )
    task = Task.objects.create(workspace=workspace, title="Tarefa compartilhada", created_by=owner)
    event = AuditEvent.objects.create(
        actor=owner,
        workspace=workspace,
        task=task,
        action=AuditEvent.Action.TASK_CREATED,
    )
    client.force_login(member)

    response = client.get(history_url(workspace, task))

    assert response.status_code == 200
    assert list(response.context["events"]) == [event]


@pytest.mark.django_db
def test_user_outside_workspace_cannot_view_task_history(client):
    owner = create_user("history-private-owner")
    outsider = create_user("history-outsider")
    workspace = Workspace.objects.create(name="Workspace privado", owner=owner)
    task = Task.objects.create(workspace=workspace, title="Não compartilhar", created_by=owner)
    client.force_login(outsider)

    response = client.get(history_url(workspace, task))

    assert response.status_code == 404


@pytest.mark.django_db
def test_member_cannot_use_another_workspace_id_to_read_task_history(client):
    owner = create_user("history-boundary-owner")
    other_owner = create_user("history-boundary-other")
    workspace = Workspace.objects.create(name="Workspace permitido", owner=owner)
    other_workspace = Workspace.objects.create(name="Workspace restrito", owner=other_owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=other_owner,
        role=WorkspaceMembership.Role.READER,
    )
    task = Task.objects.create(
        workspace=other_workspace,
        title="Tarefa fora do escopo",
        created_by=other_owner,
    )
    client.force_login(other_owner)

    response = client.get(history_url(workspace, task))

    assert response.status_code == 404


@pytest.mark.django_db
def test_owner_cannot_view_history_of_inactive_workspace(client):
    owner = create_user("history-inactive-owner")
    workspace = Workspace.objects.create(
        name="Workspace inativo",
        owner=owner,
        is_active=False,
    )
    task = Task.objects.create(workspace=workspace, title="Tarefa inativa", created_by=owner)
    client.force_login(owner)

    response = client.get(history_url(workspace, task))

    assert response.status_code == 404
