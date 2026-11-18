from datetime import date

import pytest
from django.contrib.auth import get_user_model

from apps.scheduling.models import ScheduleRule, TaskOccurrence
from apps.scheduling.services import assign_occurrence, generate_occurrences
from apps.tasks.models import Task, TaskAssignment
from apps.workspaces.models import Workspace, WorkspaceMembership


@pytest.mark.django_db
def test_weekly_rule_started_midweek_keeps_selected_weekdays():
    user = get_user_model().objects.create_user(
        username="midweek-planner",
        email="midweek-planner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Início no meio da semana", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Revisar planejamento",
        created_by=user,
    )
    rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.WEEKLY,
        starts_on=date(2026, 10, 8),  # Thursday
        weekdays=[1, 5],  # Monday and Friday
        created_by=user,
    )

    stats = generate_occurrences(rule, date(2026, 10, 8), date(2026, 10, 16))

    generated_dates = list(
        TaskOccurrence.objects.filter(task=task, schedule_rule=rule)
        .order_by("scheduled_date")
        .values_list("scheduled_date", flat=True)
    )

    assert stats["created"] == 3
    assert generated_dates == [
        date(2026, 10, 9),
        date(2026, 10, 12),
        date(2026, 10, 16),
    ]


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
def test_biweekly_rule_checks_weekdays_in_chronological_order():
    user = get_user_model().objects.create_user(
        username="biweekly-order",
        email="biweekly-order@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Ordem quinzenal", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Verificar datas quinzenais",
        created_by=user,
    )
    rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.BIWEEKLY,
        starts_on=date(2026, 10, 7),  # Wednesday
        anchor_date=date(2026, 10, 7),
        weekdays=[1, 5],  # Monday and Friday
        created_by=user,
    )

    stats = generate_occurrences(rule, date(2026, 10, 9), date(2026, 10, 10))

    generated_dates = list(
        TaskOccurrence.objects.filter(task=task, schedule_rule=rule)
        .order_by("scheduled_date")
        .values_list("scheduled_date", flat=True)
    )

    assert stats["created"] == 1
    assert generated_dates == [date(2026, 10, 9)]


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


@pytest.mark.django_db
def test_generation_applies_default_assignee_once_across_later_ranges():
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="default-owner",
        email="default-owner@example.com",
        password="Strong-password-123!",
    )
    assignee = user_model.objects.create_user(
        username="default-member",
        email="default-member@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Padrão recorrente", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=assignee,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    task = Task.objects.create(workspace=workspace, title="Tarefa semanal", created_by=owner)
    rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.WEEKLY,
        starts_on=date(2026, 10, 5),
        weekdays=[1],
        default_assignee=assignee,
        created_by=owner,
    )

    first = generate_occurrences(rule, date(2026, 10, 5), date(2026, 10, 5))
    later = generate_occurrences(rule, date(2026, 10, 12), date(2026, 10, 12))
    repeated = generate_occurrences(rule, date(2026, 10, 12), date(2026, 10, 12))

    assert first["created"] == 1
    assert later["created"] == 1
    assert repeated["created"] == 0
    assert TaskAssignment.objects.filter(
        occurrence__task=task,
        user=assignee,
    ).count() == 2


@pytest.mark.django_db
def test_generation_without_default_assignee_creates_no_assignments():
    user = get_user_model().objects.create_user(
        username="no-default",
        email="no-default@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Sem padrão", owner=user)
    task = Task.objects.create(workspace=workspace, title="Tarefa sem padrão", created_by=user)
    rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.WEEKLY,
        starts_on=date(2026, 10, 5),
        weekdays=[1],
        created_by=user,
    )

    generate_occurrences(rule, date(2026, 10, 5), date(2026, 10, 5))

    assert not TaskAssignment.objects.filter(occurrence__task=task).exists()


@pytest.mark.django_db
def test_generation_skips_inactive_default_and_preserves_existing_assignment_status():
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="inactive-default-owner",
        email="inactive-default-owner@example.com",
        password="Strong-password-123!",
    )
    assignee = user_model.objects.create_user(
        username="inactive-default-member",
        email="inactive-default-member@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Padrão inativo", owner=owner)
    membership = WorkspaceMembership.objects.create(
        workspace=workspace,
        user=assignee,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    task = Task.objects.create(workspace=workspace, title="Tarefa preservada", created_by=owner)
    rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.WEEKLY,
        starts_on=date(2026, 10, 5),
        weekdays=[1],
        default_assignee=assignee,
        created_by=owner,
    )
    existing_occurrence = TaskOccurrence.objects.create(
        task=task,
        schedule_rule=rule,
        scheduled_date=date(2026, 10, 5),
    )
    existing_assignment = TaskAssignment.objects.create(
        occurrence=existing_occurrence,
        user=assignee,
        status=TaskAssignment.Status.COMPLETED,
    )
    membership.is_active = False
    membership.save(update_fields=["is_active"])

    generate_occurrences(rule, date(2026, 10, 5), date(2026, 10, 12))

    existing_assignment.refresh_from_db()
    later_occurrence = TaskOccurrence.objects.get(task=task, scheduled_date=date(2026, 10, 12))
    assert existing_assignment.status == TaskAssignment.Status.COMPLETED
    assert not later_occurrence.assignments.filter(user=assignee).exists()


@pytest.mark.django_db
def test_assign_occurrence_is_idempotent_and_rejects_ineligible_users():
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="assignment-owner",
        email="assignment-owner@example.com",
        password="Strong-password-123!",
    )
    assignee = user_model.objects.create_user(
        username="assignment-member",
        email="assignment-member@example.com",
        password="Strong-password-123!",
    )
    external_user = user_model.objects.create_user(
        username="assignment-external",
        email="assignment-external@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Atribuição idempotente", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=assignee,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    task = Task.objects.create(workspace=workspace, title="Tarefa atribuível", created_by=owner)
    occurrence = TaskOccurrence.objects.create(
        task=task,
        scheduled_date=date(2026, 10, 5),
    )

    assignment, created = assign_occurrence(occurrence, assignee)
    assignment.status = TaskAssignment.Status.COMPLETED
    assignment.save(update_fields=["status"])
    repeated_assignment, repeated_created = assign_occurrence(occurrence, assignee)

    assert created is True
    assert repeated_created is False
    assert repeated_assignment.pk == assignment.pk
    assert repeated_assignment.status == TaskAssignment.Status.COMPLETED
    with pytest.raises(ValueError):
        assign_occurrence(occurrence, external_user)
    assert occurrence.assignments.count() == 1


@pytest.mark.django_db
def test_generation_does_not_reassign_occurrence_linked_to_another_rule():
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="rule-collision-owner",
        email="rule-collision-owner@example.com",
        password="Strong-password-123!",
    )
    assignee = user_model.objects.create_user(
        username="rule-collision-assignee",
        email="rule-collision-assignee@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Colisão entre regras", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=assignee,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    task = Task.objects.create(workspace=workspace, title="Tarefa compartilhada", created_by=owner)
    current_rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.WEEKLY,
        starts_on=date(2026, 10, 5),
        weekdays=[1],
        default_assignee=assignee,
        created_by=owner,
    )
    other_rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.MONTHLY,
        starts_on=date(2026, 10, 5),
        weekdays=[1],
        created_by=owner,
    )
    existing_occurrence = TaskOccurrence.objects.create(
        task=task,
        schedule_rule=other_rule,
        scheduled_date=date(2026, 10, 5),
    )

    generate_occurrences(current_rule, date(2026, 10, 5), date(2026, 10, 5))

    existing_occurrence.refresh_from_db()
    assert existing_occurrence.schedule_rule_id == other_rule.pk
    assert not existing_occurrence.assignments.exists()

@pytest.mark.django_db
def test_generation_does_not_assign_cancelled_occurrences():
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="cancelled-occurrence-owner",
        email="cancelled-occurrence-owner@example.com",
        password="Strong-password-123!",
    )
    assignee = user_model.objects.create_user(
        username="cancelled-occurrence-assignee",
        email="cancelled-occurrence-assignee@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Ocorrência cancelada", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=assignee,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    task = Task.objects.create(
        workspace=workspace,
        title="Não reatribuir cancelada",
        created_by=owner,
    )
    rule = ScheduleRule.objects.create(
        task=task,
        frequency=ScheduleRule.Frequency.WEEKLY,
        starts_on=date(2026, 10, 5),
        weekdays=[1],
        default_assignee=assignee,
        created_by=owner,
    )
    occurrence = TaskOccurrence.objects.create(
        task=task,
        schedule_rule=rule,
        scheduled_date=date(2026, 10, 5),
        status=TaskOccurrence.Status.CANCELLED,
    )

    stats = generate_occurrences(rule, date(2026, 10, 5), date(2026, 10, 5))

    assert stats == {"created": 0, "existing": 1, "ignored": 1}
    assert not occurrence.assignments.exists()

