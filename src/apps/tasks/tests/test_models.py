import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.tasks.models import Task, TaskAssignment
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
def test_assignment_can_be_completed_only_by_assignee():
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

    assignment.mark_completed(assignee)

    assert assignment.status == TaskAssignment.Status.COMPLETED
    assert assignment.completed_by == assignee
    assert assignment.completed_at is not None

    with pytest.raises(ValueError):
        assignment.mark_completed(owner)
