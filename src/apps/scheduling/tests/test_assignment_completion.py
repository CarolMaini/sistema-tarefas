from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from apps.scheduling.models import TaskOccurrence
from apps.tasks.models import Task, TaskAssignment, TaskExecution
from apps.workspaces.models import Workspace


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [TaskAssignment.Status.COMPLETED, TaskAssignment.Status.CANCELLED],
)
def test_inactive_assignment_cannot_be_completed_again(client, status):
    user = get_user_model().objects.create_user(
        username=f"assignee-{status}",
        email=f"assignee-{status}@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Atribuições inativas", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa concluída ou cancelada",
        created_by=user,
    )
    occurrence = TaskOccurrence.objects.create(
        task=task,
        scheduled_date=date(2026, 11, 17),
    )
    completed_at = timezone.now() if status == TaskAssignment.Status.COMPLETED else None
    assignment = TaskAssignment.objects.create(
        occurrence=occurrence,
        user=user,
        status=status,
        completed_at=completed_at,
        completed_by=user if completed_at else None,
    )
    TaskExecution.objects.create(
        assignment=assignment,
        created_by=user,
        comments="Registro de execução existente.",
    )
    client.force_login(user)

    response = client.post(
        reverse(
            "scheduling:complete-assignment",
            args=[workspace.pk, occurrence.pk, assignment.pk],
        )
    )

    assert response.status_code == 404
    assignment.refresh_from_db()
    assert assignment.status == status
    assert assignment.completed_at == completed_at
