from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.tasks.models import Task, TaskAssignment, TaskExecution
from apps.workspaces.models import Workspace


@pytest.mark.django_db
def test_task_can_be_created_inside_workspace():
    user = get_user_model().objects.create_user(
        username="planner",
        email="planner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Operações", owner=user)

    task = Task.objects.create(
        workspace=workspace,
        title="Revisar cronograma",
        description="Validar os prazos da semana.",
        created_by=user,
    )

    assert str(task) == "Revisar cronograma"
    assert task.status == Task.Status.ACTIVE
    assert task.workspace == workspace


@pytest.mark.django_db
def test_assignment_is_unique_per_occurrence_and_user():
    user = get_user_model().objects.create_user(
        username="assignee",
        email="assignee@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Marketing", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Preparar campanha",
        created_by=user,
    )
    occurrence = task.occurrences.create(
        scheduled_date="2026-10-12",
        starts_at="09:00:00",
    )

    TaskAssignment.objects.create(
        occurrence=occurrence,
        user=user,
    )

    with pytest.raises(IntegrityError):
        TaskAssignment.objects.create(
            occurrence=occurrence,
            user=user,
        )


@pytest.mark.django_db
def test_assignment_can_be_completed_only_by_assignee_after_execution():
    owner = get_user_model().objects.create_user(
        username="owner",
        email="owner@example.com",
        password="Strong-password-123!",
    )
    assignee = get_user_model().objects.create_user(
        username="assignee",
        email="assignee2@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Suporte", owner=owner)
    task = Task.objects.create(
        workspace=workspace,
        title="Responder tickets",
        created_by=owner,
    )
    occurrence = task.occurrences.create(
        scheduled_date="2026-10-13",
        starts_at="10:00:00",
    )
    assignment = TaskAssignment.objects.create(
        occurrence=occurrence,
        user=assignee,
    )
    TaskExecution.objects.create(
        assignment=assignment,
        created_by=assignee,
        comments="Tickets respondidos.",
    )

    assignment.mark_completed(assignee)

    assert assignment.status == TaskAssignment.Status.COMPLETED
    assert assignment.completed_by == assignee
    assert assignment.completed_at is not None

    with pytest.raises(ValueError, match="Only the assignee"):
        assignment.mark_completed(owner)


@pytest.mark.django_db
def test_assignment_cannot_be_completed_without_execution():
    user = get_user_model().objects.create_user(
        username="no-execution",
        email="no-execution@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Sem execução", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa sem registro",
        created_by=user,
    )
    occurrence = task.occurrences.create(scheduled_date="2026-11-18")
    assignment = TaskAssignment.objects.create(occurrence=occurrence, user=user)

    with pytest.raises(ValueError, match="requires an execution record"):
        assignment.mark_completed(user)

    assignment.refresh_from_db()
    assert assignment.status == TaskAssignment.Status.PENDING
    assert assignment.completed_at is None
    assert assignment.completed_by is None


@pytest.mark.django_db
def test_execution_cannot_be_saved_when_end_precedes_start():
    user = get_user_model().objects.create_user(
        username="invalid-execution-time",
        email="invalid-execution-time@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Execução inválida", owner=user)
    task = Task.objects.create(workspace=workspace, title="Tarefa", created_by=user)
    occurrence = task.occurrences.create(scheduled_date="2026-11-18")
    assignment = TaskAssignment.objects.create(occurrence=occurrence, user=user)
    started_at = timezone.now()

    with pytest.raises(ValidationError, match="posterior ao início"):
        TaskExecution.objects.create(
            assignment=assignment,
            created_by=user,
            started_at=started_at,
            ended_at=started_at - timedelta(minutes=1),
        )

    assert not TaskExecution.objects.filter(assignment=assignment).exists()


@pytest.mark.django_db
def test_execution_cannot_be_created_by_user_other_than_assignee():
    user_model = get_user_model()
    assignee = user_model.objects.create_user(
        username="execution-assignee",
        email="execution-assignee@example.com",
        password="Strong-password-123!",
    )
    other_user = user_model.objects.create_user(
        username="execution-outsider",
        email="execution-outsider@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Autoria da execução", owner=assignee)
    task = Task.objects.create(workspace=workspace, title="Tarefa", created_by=assignee)
    occurrence = task.occurrences.create(scheduled_date="2026-11-19")
    assignment = TaskAssignment.objects.create(occurrence=occurrence, user=assignee)

    with pytest.raises(ValidationError, match="responsável pela atribuição"):
        TaskExecution.objects.create(
            assignment=assignment,
            created_by=other_user,
            comments="Tentativa de registrar execução em nome de outra pessoa.",
        )

    assert not TaskExecution.objects.filter(assignment=assignment).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [TaskAssignment.Status.COMPLETED, TaskAssignment.Status.CANCELLED],
)
def test_inactive_assignment_cannot_be_completed_again(status):
    user = get_user_model().objects.create_user(
        username=f"inactive-{status}",
        email=f"inactive-{status}@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Atribuições", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa",
        created_by=user,
    )
    occurrence = task.occurrences.create(scheduled_date="2026-11-17")
    assignment = TaskAssignment.objects.create(
        occurrence=occurrence,
        user=user,
        status=status,
    )
    original_completed_at = assignment.completed_at

    with pytest.raises(ValueError):
        assignment.mark_completed(user)

    assignment.refresh_from_db()
    assert assignment.status == status
    assert assignment.completed_at == original_completed_at
