import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.audit.models import AuditEvent
from apps.scheduling.models import TaskOccurrence
from apps.tasks.models import Task, TaskAssignment, TaskExecution
from apps.workspaces.models import Workspace


@pytest.fixture
def task_context():
    user = get_user_model().objects.create_user(
        username="audit-actor",
        email="audit-actor@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Auditoria", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa auditável",
        created_by=user,
    )
    occurrence = TaskOccurrence.objects.create(
        task=task,
        scheduled_date="2026-11-20",
    )
    assignment = TaskAssignment.objects.create(
        occurrence=occurrence,
        user=user,
    )
    return user, workspace, task, occurrence, assignment


@pytest.mark.django_db
def test_task_creation_is_audited(client, task_context):
    user, workspace, task, _, _ = task_context
    task.delete()
    client.force_login(user)

    response = client.post(
        reverse("tasks:create", kwargs={"workspace_id": workspace.pk}),
        {"title": "Nova tarefa", "description": "Criada com trilha."},
    )

    created_task = Task.objects.get(workspace=workspace, title="Nova tarefa")
    event = AuditEvent.objects.get(
        action=AuditEvent.Action.TASK_CREATED,
        task=created_task,
    )
    assert response.status_code == 302
    assert event.actor == user
    assert event.workspace == workspace
    assert event.target_user is None


@pytest.mark.django_db
def test_task_update_is_audited(client, task_context):
    user, workspace, task, _, _ = task_context
    client.force_login(user)

    response = client.post(
        reverse("tasks:update", kwargs={"workspace_id": workspace.pk, "task_id": task.pk}),
        {"title": "Título auditado", "description": ""},
    )

    event = AuditEvent.objects.get(
        action=AuditEvent.Action.TASK_UPDATED,
        task=task,
    )
    assert response.status_code == 302
    assert event.actor == user
    assert event.workspace == workspace


@pytest.mark.django_db
def test_task_archive_is_audited_once(client, task_context):
    user, workspace, task, _, _ = task_context
    client.force_login(user)
    url = reverse("tasks:archive", kwargs={"workspace_id": workspace.pk, "task_id": task.pk})

    first_response = client.post(url)
    second_response = client.post(url)

    assert first_response.status_code == 302
    assert second_response.status_code == 302
    assert AuditEvent.objects.filter(
        action=AuditEvent.Action.TASK_ARCHIVED,
        task=task,
    ).count() == 1


@pytest.mark.django_db
def test_assignment_creation_is_audited(client, task_context):
    user, workspace, task, occurrence, assignment = task_context
    assignment.delete()
    client.force_login(user)

    response = client.post(
        reverse("scheduling:occurrence-assign", args=[workspace.pk, occurrence.pk]),
        {"user": user.pk},
    )

    created_assignment = TaskAssignment.objects.get(occurrence=occurrence, user=user)
    event = AuditEvent.objects.get(
        action=AuditEvent.Action.TASK_ASSIGNMENT_CREATED,
        assignment=created_assignment,
    )
    assert response.status_code == 302
    assert event.actor == user
    assert event.target_user == user
    assert event.task == task


@pytest.mark.django_db
def test_execution_creation_is_audited(client, task_context):
    user, workspace, task, occurrence, assignment = task_context
    client.force_login(user)

    response = client.post(
        reverse("scheduling:occurrence-detail", args=[workspace.pk, occurrence.pk]),
        {
            "assignment_id": assignment.pk,
            "started_at": "2026-11-20T09:00",
            "ended_at": "2026-11-20T09:30",
            "comments": "Execução registrada.",
        },
    )

    execution = TaskExecution.objects.get(assignment=assignment)
    event = AuditEvent.objects.get(
        action=AuditEvent.Action.TASK_EXECUTION_CREATED,
        execution=execution,
    )
    assert response.status_code == 302
    assert event.actor == user
    assert event.workspace == workspace
    assert event.task == task
    assert event.assignment == assignment


@pytest.mark.django_db
def test_assignment_completion_is_audited(client, task_context):
    user, workspace, task, occurrence, assignment = task_context
    TaskExecution.objects.create(
        assignment=assignment,
        created_by=user,
        comments="Execução prévia.",
    )
    client.force_login(user)

    response = client.post(
        reverse(
            "scheduling:complete-assignment",
            args=[workspace.pk, occurrence.pk, assignment.pk],
        )
    )

    event = AuditEvent.objects.get(
        action=AuditEvent.Action.TASK_ASSIGNMENT_COMPLETED,
        assignment=assignment,
    )
    assert response.status_code == 302
    assert event.actor == user
    assert event.target_user == user
    assert event.task == task
