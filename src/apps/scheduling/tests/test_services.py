from datetime import date

import pytest
from django.contrib.auth import get_user_model

from apps.scheduling.models import ScheduleRule, TaskOccurrence
from apps.scheduling.services import generate_occurrences
from apps.tasks.models import Task
from apps.workspaces.models import Workspace


@pytest.mark.django_db
def test_weekly_rule_generates_occurrences_for_selected_days():
    user = get_user_model().objects.create_user(
        username="planner",
        email="planner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Planejamento", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Revisar backlog",
        created_by=user,
    )
    rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.WEEKLY,
        starts_on=date(2026, 10, 5),
        weekdays=[1, 5],
        created_by=user,
    )

    stats = generate_occurrences(rule, date(2026, 10, 5), date(2026, 10, 15))

    assert stats["created"] >= 3
    assert TaskOccurrence.objects.filter(task=task, schedule_rule=rule).exists()


@pytest.mark.django_db
def test_biweekly_rule_is_idempotent_and_uses_anchor_date():
    user = get_user_model().objects.create_user(
        username="anchor",
        email="anchor@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Operações", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Acompanhar folga",
        created_by=user,
    )
    rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.BIWEEKLY,
        starts_on=date(2026, 10, 1),
        anchor_date=date(2026, 10, 1),
        weekdays=[5],
        created_by=user,
    )

    end_date = date(2026, 10, 30)
    first = generate_occurrences(rule, rule.starts_on, end_date)
    second = generate_occurrences(rule, rule.starts_on, end_date)

    assert first["created"] > 0
    assert second["created"] == 0
    assert TaskOccurrence.objects.filter(task=task, schedule_rule=rule).count() == first["created"]


@pytest.mark.django_db
def test_monthly_rule_generates_weekend_occurrences():
    user = get_user_model().objects.create_user(
        username="month",
        email="month@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Mensal", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Revisão mensal",
        created_by=user,
    )
    rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.MONTHLY,
        starts_on=date(2026, 10, 1),
        weekdays=[6, 7],
        created_by=user,
    )

    stats = generate_occurrences(rule, date(2026, 10, 1), date(2026, 10, 31))

    assert stats["created"] >= 2
    assert TaskOccurrence.objects.filter(task=task, schedule_rule=rule).count() == stats["created"]
