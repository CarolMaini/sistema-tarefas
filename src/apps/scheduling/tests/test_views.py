from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.scheduling.models import ScheduleRule, TaskOccurrence
from apps.tasks.models import Task
from apps.workspaces.models import Workspace


@pytest.mark.django_db
def test_workspace_calendar_view_lists_occurrences_for_the_month(client):
    user = get_user_model().objects.create_user(
        username="calendar-user",
        email="calendar@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Calendário", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Revisão do calendário",
        created_by=user,
    )
    ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.WEEKLY,
        starts_on=date(2026, 10, 1),
        weekdays=[2, 5],
        created_by=user,
    )
    TaskOccurrence.objects.create(
        task=task,
        schedule_rule=None,
        scheduled_date=date(2026, 10, 6),
    )

    client.force_login(user)
    response = client.get(
        reverse("scheduling:calendar", args=[workspace.pk]),
        {"year": 2026, "month": 10},
    )

    assert response.status_code == 200
    assert "Revisão do calendário" in response.content.decode()
    assert "outubro" in response.content.decode().lower()


@pytest.mark.django_db
def test_occurrence_detail_allows_own_assignment_completion(client):
    user = get_user_model().objects.create_user(
        username="occurrence-user",
        email="occurrence@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Execução", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa de execução",
        created_by=user,
    )
    occurrence = TaskOccurrence.objects.create(
        task=task,
        schedule_rule=None,
        scheduled_date=date(2026, 10, 20),
    )
    assignment = occurrence.assignments.create(
        user=user,
        status="pending",
    )

    client.force_login(user)
    detail_response = client.get(
        reverse("scheduling:occurrence-detail", args=[workspace.pk, occurrence.pk]),
    )
    assert detail_response.status_code == 200
    assert "Tarefa de execução" in detail_response.content.decode()

    completion_response = client.post(
        reverse(
            "scheduling:complete-assignment",
            args=[workspace.pk, occurrence.pk, assignment.pk],
        )
    )

    assert completion_response.status_code == 302
    assignment.refresh_from_db()
    assert assignment.status == "completed"


@pytest.mark.django_db
def test_occurrence_can_be_assigned_to_workspace_member(client):
    owner = get_user_model().objects.create_user(
        username="owner-user",
        email="owner@example.com",
        password="Strong-password-123!",
    )
    assignee = get_user_model().objects.create_user(
        username="assignee-user",
        email="assignee@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Atribuição", owner=owner)
    workspace.memberships.create(user=assignee, role="collaborator")
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa atribuída",
        created_by=owner,
    )
    occurrence = TaskOccurrence.objects.create(
        task=task,
        schedule_rule=None,
        scheduled_date=date(2026, 10, 25),
    )

    client.force_login(owner)
    response = client.post(
        reverse("scheduling:occurrence-assign", args=[workspace.pk, occurrence.pk]),
        {"user": assignee.pk},
    )

    assert response.status_code == 302
    assert occurrence.assignments.filter(user=assignee).exists()


@pytest.mark.django_db
def test_recurrence_creation_can_assign_default_responsible(client):
    user = get_user_model().objects.create_user(
        username="manager-user",
        email="manager@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Recorrência com responsável", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Entrega recorrente",
        created_by=user,
    )

    client.force_login(user)
    response = client.post(
        reverse("scheduling:create", args=[workspace.pk, task.pk]),
        {
            "frequency": ScheduleRule.Frequency.WEEKLY,
            "starts_on": "2026-10-05",
            "ends_on": "2026-10-19",
            "weekdays": ["1", "5"],
            "anchor_date": "2026-10-05",
            "assignee": user.pk,
        },
    )

    assert response.status_code == 302
    occurrences = TaskOccurrence.objects.filter(task=task)
    assert occurrences.exists()
    assert occurrences.filter(assignments__user=user).exists()


@pytest.mark.django_db
def test_task_list_shows_generated_occurrences_and_allows_rule_creation(client):
    user = get_user_model().objects.create_user(
        username="recurrence-user",
        email="recurrence@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Recorrência", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Planejamento semanal",
        created_by=user,
    )

    client.force_login(user)
    response = client.post(
        reverse("scheduling:create", args=[workspace.pk, task.pk]),
        {
            "frequency": ScheduleRule.Frequency.WEEKLY,
            "starts_on": "2026-10-05",
            "ends_on": "2026-10-19",
            "weekdays": ["1", "5"],
            "anchor_date": "2026-10-05",
        },
    )

    assert response.status_code == 302
    assert ScheduleRule.objects.filter(task=task).count() == 1
    assert TaskOccurrence.objects.filter(task=task).count() >= 2

    list_response = client.get(reverse("tasks:list", args=[workspace.pk]))
    assert list_response.status_code == 200
    html = list_response.content.decode()
    assert "Planejamento semanal" in html
    assert "Próximas ocorrências" in html
