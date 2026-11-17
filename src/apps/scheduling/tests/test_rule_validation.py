from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.scheduling.models import ScheduleRule
from apps.tasks.models import Task
from apps.workspaces.models import Workspace


@pytest.fixture
def schedule_rule_context():
    user = get_user_model().objects.create_user(
        username="schedule-rule-validation",
        email="schedule-rule-validation@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Validação de recorrência", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa recorrente",
        created_by=user,
    )
    return {"user": user, "task": task}


@pytest.mark.django_db
def test_schedule_rule_rejects_end_date_before_start_date_on_save(schedule_rule_context):
    with pytest.raises(ValidationError, match="igual ou posterior"):
        ScheduleRule.objects.create(
            task=schedule_rule_context["task"],
            starts_on=date(2026, 11, 20),
            ends_on=date(2026, 11, 19),
            weekdays=[1, 5],
            created_by=schedule_rule_context["user"],
        )

    assert not ScheduleRule.objects.filter(task=schedule_rule_context["task"]).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("weekdays", [[0], [8], [1, 8], ["1"], [True], "1,5", None])
def test_schedule_rule_rejects_invalid_weekday_values_on_save(
    schedule_rule_context, weekdays
):
    with pytest.raises(ValidationError, match="dias da semana"):
        ScheduleRule.objects.create(
            task=schedule_rule_context["task"],
            starts_on=date(2026, 11, 17),
            weekdays=weekdays,
            created_by=schedule_rule_context["user"],
        )

    assert not ScheduleRule.objects.filter(task=schedule_rule_context["task"]).exists()


@pytest.mark.django_db
def test_schedule_rule_accepts_empty_weekdays_for_legacy_default_behavior(
    schedule_rule_context,
):
    rule = ScheduleRule.objects.create(
        task=schedule_rule_context["task"],
        starts_on=date(2026, 11, 17),
        weekdays=[],
        created_by=schedule_rule_context["user"],
    )

    assert rule.weekdays == []
