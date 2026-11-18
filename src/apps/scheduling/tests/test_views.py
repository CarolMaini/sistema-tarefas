from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from apps.scheduling.models import ScheduleRule, TaskOccurrence
from apps.tasks.models import Task, TaskAssignment, TaskExecution
from apps.workspaces.models import Workspace, WorkspaceMembership


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
@pytest.mark.parametrize(
    ("query", "value"),
    [
        ("year", "not-a-year"),
        ("year", "0"),
        ("year", "10000"),
        ("month", "not-a-month"),
        ("month", "13"),
    ],
)
def test_workspace_calendar_rejects_invalid_date_parameters(client, query, value):
    user = get_user_model().objects.create_user(
        username=f"invalid-calendar-{query}-{value}".replace("-", ""),
        email=f"invalid-calendar-{query}-{value}@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Calendário inválido", owner=user)
    client.force_login(user)

    response = client.get(
        reverse("scheduling:calendar", args=[workspace.pk]),
        {query: value},
    )

    assert response.status_code == 404


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
    assert assignment.status == "pending"

    execution_response = client.post(
        reverse("scheduling:occurrence-detail", args=[workspace.pk, occurrence.pk]),
        {
            "assignment_id": assignment.pk,
            "started_at": "2026-10-20T09:00",
            "ended_at": "2026-10-20T10:00",
            "comments": "Execução concluída.",
        },
    )
    assert execution_response.status_code == 302

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
def test_occurrence_detail_lists_each_assignee_status_and_empty_state(client):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="detail-owner",
        email="detail-owner@example.com",
        password="Strong-password-123!",
    )
    pending_user = user_model.objects.create_user(
        username="detail-pending",
        email="detail-pending@example.com",
        password="Strong-password-123!",
    )
    completed_user = user_model.objects.create_user(
        username="detail-completed",
        email="detail-completed@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Detalhe das atribuições", owner=owner)
    workspace.memberships.create(user=pending_user, role="collaborator")
    workspace.memberships.create(user=completed_user, role="collaborator")
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa com responsáveis",
        created_by=owner,
    )
    occurrence = TaskOccurrence.objects.create(task=task, scheduled_date=date(2026, 10, 29))
    occurrence.assignments.create(user=pending_user, status=TaskAssignment.Status.PENDING)
    occurrence.assignments.create(user=completed_user, status=TaskAssignment.Status.COMPLETED)
    empty_occurrence = TaskOccurrence.objects.create(
        task=task,
        scheduled_date=date(2026, 10, 30),
    )
    client.force_login(owner)

    response = client.get(
        reverse("scheduling:occurrence-detail", args=[workspace.pk, occurrence.pk]),
    )
    empty_response = client.get(
        reverse("scheduling:occurrence-detail", args=[workspace.pk, empty_occurrence.pk]),
    )

    assert response.status_code == 200
    detail_html = response.content.decode()
    assert "detail-pending" in detail_html
    assert "detail-completed" in detail_html
    assert "Pendente" in detail_html
    assert "Concluída" in detail_html
    assert "Nenhuma atribuição registrada para esta ocorrência." in empty_response.content.decode()


@pytest.mark.django_db
def test_assignee_can_record_execution_with_comments_and_private_attachment(
    client, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    user = get_user_model().objects.create_user(
        username="execution-user",
        email="execution@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Execução detalhada", owner=user)
    task = Task.objects.create(workspace=workspace, title="Preparar relatório", created_by=user)
    occurrence = TaskOccurrence.objects.create(
        task=task,
        schedule_rule=None,
        scheduled_date=date(2026, 10, 12),
    )
    assignment = occurrence.assignments.create(user=user)
    client.force_login(user)

    response = client.post(
        reverse("scheduling:occurrence-detail", args=[workspace.pk, occurrence.pk]),
        {
            "assignment_id": assignment.pk,
            "started_at": "2026-10-12T09:00",
            "ended_at": "2026-10-12T10:30",
            "comments": "Relatório revisado e enviado.",
            "attachment": SimpleUploadedFile(
                "evidencia.pdf",
                b"%PDF-1.4\nEvidence\n%%EOF",
                content_type="application/pdf",
            ),
        },
    )

    assert response.status_code == 302
    execution = TaskExecution.objects.get(assignment=assignment)
    assert execution.comments == "Relatório revisado e enviado."
    assert timezone.localtime(execution.started_at).hour == 9
    assert timezone.localtime(execution.ended_at).hour == 10
    assert execution.attachment.name.startswith("task-executions/")
    assignment.refresh_from_db()
    assert assignment.status == TaskAssignment.Status.PENDING

    attachment_url = reverse(
        "scheduling:execution-attachment",
        args=[workspace.pk, occurrence.pk, execution.pk],
    )
    assert client.get(attachment_url).status_code == 200

    outsider = get_user_model().objects.create_user(
        username="execution-outsider",
        email="execution-outsider@example.com",
        password="Strong-password-123!",
    )
    client.force_login(outsider)
    assert client.get(attachment_url).status_code == 404


@pytest.mark.django_db
def test_execution_rejects_end_time_before_start_time(client):
    user = get_user_model().objects.create_user(
        username="invalid-execution-user",
        email="invalid-execution@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Horários", owner=user)
    task = Task.objects.create(workspace=workspace, title="Conferir horários", created_by=user)
    occurrence = TaskOccurrence.objects.create(
        task=task,
        schedule_rule=None,
        scheduled_date=date(2026, 10, 12),
    )
    assignment = occurrence.assignments.create(user=user)
    client.force_login(user)

    response = client.post(
        reverse("scheduling:occurrence-detail", args=[workspace.pk, occurrence.pk]),
        {
            "assignment_id": assignment.pk,
            "started_at": "2026-10-12T10:00",
            "ended_at": "2026-10-12T09:00",
            "comments": "Horários inválidos.",
        },
    )

    assert response.status_code == 400
    assert TaskExecution.objects.count() == 0


@pytest.mark.django_db
def test_assignee_cannot_record_execution_for_another_member(client):
    owner = get_user_model().objects.create_user(
        username="execution-owner",
        email="execution-owner@example.com",
        password="Strong-password-123!",
    )
    assignee = get_user_model().objects.create_user(
        username="execution-assignee",
        email="execution-assignee@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Execução restrita", owner=owner)
    task = Task.objects.create(workspace=workspace, title="Ação restrita", created_by=owner)
    occurrence = TaskOccurrence.objects.create(
        task=task,
        schedule_rule=None,
        scheduled_date=date(2026, 10, 12),
    )
    assignment = occurrence.assignments.create(user=assignee)
    client.force_login(owner)

    response = client.post(
        reverse("scheduling:occurrence-detail", args=[workspace.pk, occurrence.pk]),
        {
            "assignment_id": assignment.pk,
            "started_at": "2026-10-12T09:00",
            "ended_at": "2026-10-12T10:00",
            "comments": "Tentativa indevida.",
        },
    )

    assert response.status_code == 404
    assert not TaskExecution.objects.exists()


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
def test_workspace_manager_can_assign_occurrence_to_member(client):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="assign-manager-owner",
        email="assign-manager-owner@example.com",
        password="Strong-password-123!",
    )
    manager = user_model.objects.create_user(
        username="assign-manager",
        email="assign-manager@example.com",
        password="Strong-password-123!",
    )
    assignee = user_model.objects.create_user(
        username="assign-manager-target",
        email="assign-manager-target@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Gestor atribui", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=manager,
        role=WorkspaceMembership.Role.MANAGER,
    )
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=assignee,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    task = Task.objects.create(workspace=workspace, title="Tarefa do gestor", created_by=owner)
    occurrence = TaskOccurrence.objects.create(task=task, scheduled_date=date(2026, 10, 28))
    client.force_login(manager)

    response = client.post(
        reverse("scheduling:occurrence-assign", args=[workspace.pk, occurrence.pk]),
        {"user": assignee.pk},
    )

    assert response.status_code == 302
    assert occurrence.assignments.filter(user=assignee).exists()


@pytest.mark.django_db
def test_collaborator_can_assign_occurrence_to_another_member(client):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="assign-collab-owner",
        email="assign-collab-owner@example.com",
        password="Strong-password-123!",
    )
    collaborator = user_model.objects.create_user(
        username="assign-collab",
        email="assign-collab@example.com",
        password="Strong-password-123!",
    )
    assignee = user_model.objects.create_user(
        username="assign-collab-target",
        email="assign-collab-target@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Colaborador atribui", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=collaborator,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=assignee,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    task = Task.objects.create(workspace=workspace, title="Tarefa compartilhada", created_by=owner)
    occurrence = TaskOccurrence.objects.create(task=task, scheduled_date=date(2026, 10, 29))
    detail_url = reverse("scheduling:occurrence-detail", args=[workspace.pk, occurrence.pk])
    client.force_login(collaborator)

    detail_response = client.get(detail_url)
    post_response = client.post(
        reverse("scheduling:occurrence-assign", args=[workspace.pk, occurrence.pk]),
        {"user": assignee.pk},
    )

    assert detail_response.status_code == 200
    assert "Atribuir responsável" in detail_response.content.decode()
    assert post_response.status_code == 302
    assert occurrence.assignments.filter(user=assignee).exists()

@pytest.mark.django_db
def test_occurrence_can_be_assigned_to_workspace_owner(client):
    owner = get_user_model().objects.create_user(
        username="assign-owner",
        email="assign-owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Responsável proprietário", owner=owner)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa do proprietário",
        created_by=owner,
    )
    occurrence = TaskOccurrence.objects.create(
        task=task,
        scheduled_date=date(2026, 10, 25),
    )
    client.force_login(owner)

    response = client.post(
        reverse("scheduling:occurrence-assign", args=[workspace.pk, occurrence.pk]),
        {"user": owner.pk},
    )

    assert response.status_code == 302
    assert occurrence.assignments.filter(user=owner).exists()


@pytest.mark.django_db
def test_occurrence_assignment_rejects_external_and_inactive_users(client):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="assignment-validation-owner",
        email="assignment-validation-owner@example.com",
        password="Strong-password-123!",
    )
    inactive_user = user_model.objects.create_user(
        username="assignment-inactive",
        email="assignment-inactive@example.com",
        password="Strong-password-123!",
    )
    external_user = user_model.objects.create_user(
        username="assignment-outsider",
        email="assignment-outsider@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Elegibilidade manual", owner=owner)
    workspace.memberships.create(
        user=inactive_user,
        role="collaborator",
        is_active=False,
    )
    task = Task.objects.create(workspace=workspace, title="Tarefa manual", created_by=owner)
    occurrence = TaskOccurrence.objects.create(task=task, scheduled_date=date(2026, 10, 26))
    client.force_login(owner)

    for ineligible_user in (external_user, inactive_user):
        response = client.post(
            reverse("scheduling:occurrence-assign", args=[workspace.pk, occurrence.pk]),
            {"user": ineligible_user.pk},
        )
        assert response.status_code == 404

    assert occurrence.assignments.count() == 0


@pytest.mark.django_db
def test_repeated_occurrence_assignment_preserves_status_and_shows_feedback(client):
    owner = get_user_model().objects.create_user(
        username="duplicate-assignment-owner",
        email="duplicate-assignment-owner@example.com",
        password="Strong-password-123!",
    )
    assignee = get_user_model().objects.create_user(
        username="duplicate-assignee",
        email="duplicate-assignee@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Atribuição repetida", owner=owner)
    workspace.memberships.create(user=assignee, role="collaborator")
    task = Task.objects.create(workspace=workspace, title="Tarefa repetida", created_by=owner)
    occurrence = TaskOccurrence.objects.create(task=task, scheduled_date=date(2026, 10, 27))
    assignment = occurrence.assignments.create(
        user=assignee,
        status=TaskAssignment.Status.COMPLETED,
    )
    client.force_login(owner)

    response = client.post(
        reverse("scheduling:occurrence-assign", args=[workspace.pk, occurrence.pk]),
        {"user": assignee.pk},
        follow=True,
    )

    assignment.refresh_from_db()
    assert response.status_code == 200
    assert "já está atribuído" in response.content.decode()
    assert occurrence.assignments.count() == 1
    assert assignment.status == TaskAssignment.Status.COMPLETED


@pytest.mark.django_db
def test_actor_without_task_management_permission_cannot_assign_occurrence(client):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="permission-owner",
        email="permission-owner@example.com",
        password="Strong-password-123!",
    )
    reader = user_model.objects.create_user(
        username="permission-reader",
        email="permission-reader@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Atribuição autorizada", owner=owner)
    workspace.memberships.create(user=reader, role="reader")
    task = Task.objects.create(workspace=workspace, title="Tarefa protegida", created_by=owner)
    occurrence = TaskOccurrence.objects.create(task=task, scheduled_date=date(2026, 10, 28))
    client.force_login(reader)

    response = client.post(
        reverse("scheduling:occurrence-assign", args=[workspace.pk, occurrence.pk]),
        {"user": owner.pk},
    )

    assert response.status_code == 404
    assert occurrence.assignments.count() == 0


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
            "default_assignee": user.pk,
        },
    )

    assert response.status_code == 302
    rule = ScheduleRule.objects.get(task=task)
    assert rule.default_assignee_id == user.pk
    occurrences = TaskOccurrence.objects.filter(task=task)
    assert occurrences.exists()
    assert occurrences.filter(assignments__user=user).exists()


@pytest.mark.django_db
def test_recurrence_creation_rejects_external_default_assignee(client):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="recurrence-owner",
        email="recurrence-owner@example.com",
        password="Strong-password-123!",
    )
    external_user = user_model.objects.create_user(
        username="recurrence-external",
        email="recurrence-external@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Recorrência validada", owner=owner)
    task = Task.objects.create(workspace=workspace, title="Tarefa validada", created_by=owner)
    client.force_login(owner)

    response = client.post(
        reverse("scheduling:create", args=[workspace.pk, task.pk]),
        {
            "frequency": ScheduleRule.Frequency.WEEKLY,
            "starts_on": "2026-10-05",
            "ends_on": "2026-10-19",
            "weekdays": ["1"],
            "anchor_date": "2026-10-05",
            "default_assignee": external_user.pk,
        },
    )

    assert response.status_code == 200
    assert not ScheduleRule.objects.filter(task=task).exists()
    assert not TaskOccurrence.objects.filter(task=task).exists()


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


@pytest.mark.django_db
def test_recurrence_creation_rolls_back_rule_when_occurrence_generation_fails(
    client, monkeypatch
):
    user = get_user_model().objects.create_user(
        username="atomic-recurrence-user",
        email="atomic-recurrence@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Recorrência atômica", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa com geração protegida",
        created_by=user,
    )

    def fail_generation(*args, **kwargs):
        raise RuntimeError("Falha simulada na geração de ocorrências.")

    monkeypatch.setattr(
        "apps.scheduling.views.generate_occurrences",
        fail_generation,
    )
    client.force_login(user)

    with pytest.raises(RuntimeError, match="Falha simulada"):
        client.post(
            reverse("scheduling:create", args=[workspace.pk, task.pk]),
            {
                "frequency": ScheduleRule.Frequency.WEEKLY,
                "starts_on": "2026-11-16",
                "ends_on": "2026-11-30",
                "weekdays": ["1", "5"],
                "anchor_date": "2026-11-16",
            },
        )

    assert not ScheduleRule.objects.filter(task=task).exists()
    assert not TaskOccurrence.objects.filter(task=task).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("year", "month", "available_link", "unavailable_label"),
    [
        (1, 1, "?year=1&month=2", "Anterior"),
        (9999, 12, "?year=9999&month=11", "Próximo"),
    ],
)
def test_workspace_calendar_disables_navigation_beyond_supported_years(
    client, year, month, available_link, unavailable_label
):
    user = get_user_model().objects.create_user(
        username=f"calendar-boundary-{year}",
        email=f"calendar-boundary-{year}@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Limites do calendário", owner=user)
    client.force_login(user)

    response = client.get(
        reverse("scheduling:calendar", args=[workspace.pk]),
        {"year": year, "month": month},
    )

    html = response.content.decode()
    assert response.status_code == 200
    assert available_link in html
    assert f'aria-disabled="true">{unavailable_label}</span>' in html


@pytest.mark.django_db
def test_recurrence_creation_rejects_end_date_before_start_date(client):
    user = get_user_model().objects.create_user(
        username="invalid-recurrence-range",
        email="invalid-recurrence-range@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Intervalo inválido", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Recorrência com intervalo inválido",
        created_by=user,
    )
    client.force_login(user)

    response = client.post(
        reverse("scheduling:create", args=[workspace.pk, task.pk]),
        {
            "frequency": ScheduleRule.Frequency.WEEKLY,
            "starts_on": "2026-11-20",
            "ends_on": "2026-11-19",
            "weekdays": ["1", "5"],
            "anchor_date": "2026-11-20",
        },
    )

    assert response.status_code == 200
    assert (
        "A data de término deve ser igual ou posterior à data de início."
        in response.content.decode()
    )
    assert not ScheduleRule.objects.filter(task=task).exists()
    assert not TaskOccurrence.objects.filter(task=task).exists()


@pytest.mark.django_db
def test_inactive_workspace_member_cannot_download_execution_attachment(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="attachment-access-owner",
        email="attachment-access-owner@example.com",
        password="Strong-password-123!",
    )
    former_member = user_model.objects.create_user(
        username="attachment-former-member",
        email="attachment-former-member@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Anexo restrito", owner=owner)
    membership = WorkspaceMembership.objects.create(
        workspace=workspace,
        user=former_member,
        role=WorkspaceMembership.Role.READER,
        is_active=False,
    )
    task = Task.objects.create(workspace=workspace, title="Evidência", created_by=owner)
    occurrence = TaskOccurrence.objects.create(task=task, scheduled_date=date(2026, 11, 17))
    assignment = occurrence.assignments.create(user=owner)
    execution = TaskExecution.objects.create(
        assignment=assignment,
        created_by=owner,
        attachment=SimpleUploadedFile(
            "evidence.pdf",
            b"%PDF-1.4\\nEvidence\\n%%EOF",
            content_type="application/pdf",
        ),
    )
    attachment_url = reverse(
        "scheduling:execution-attachment",
        args=[workspace.pk, occurrence.pk, execution.pk],
    )
    client.force_login(former_member)

    response = client.get(attachment_url)

    assert not membership.is_active
    assert response.status_code == 404


@pytest.mark.django_db
def test_execution_attachment_cannot_be_accessed_through_another_workspace(
    client, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="attachment-owner",
        email="attachment-owner@example.com",
        password="Strong-password-123!",
    )
    other_owner = user_model.objects.create_user(
        username="attachment-other-owner",
        email="attachment-other-owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Workspace original", owner=owner)
    other_workspace = Workspace.objects.create(name="Outro workspace", owner=other_owner)
    task = Task.objects.create(workspace=workspace, title="Evidência", created_by=owner)
    occurrence = TaskOccurrence.objects.create(task=task, scheduled_date=date(2026, 11, 17))
    assignment = occurrence.assignments.create(user=owner)
    execution = TaskExecution.objects.create(
        assignment=assignment,
        created_by=owner,
        attachment=SimpleUploadedFile(
            "evidence.pdf",
            b"%PDF-1.4\\nEvidence\\n%%EOF",
            content_type="application/pdf",
        ),
    )
    attachment_url = reverse(
        "scheduling:execution-attachment",
        args=[other_workspace.pk, occurrence.pk, execution.pk],
    )
    client.force_login(other_owner)

    response = client.get(attachment_url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_archived_task_cannot_create_new_recurrence(client):
    user = get_user_model().objects.create_user(
        username="archived-recurrence-owner",
        email="archived-recurrence-owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Recorrência arquivada", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa arquivada",
        created_by=user,
        status=Task.Status.ARCHIVED,
    )
    client.force_login(user)

    response = client.post(
        reverse("scheduling:create", args=[workspace.pk, task.pk]),
        {
            "frequency": ScheduleRule.Frequency.WEEKLY,
            "starts_on": "2026-11-17",
            "ends_on": "2026-11-30",
            "weekdays": ["1", "5"],
            "anchor_date": "2026-11-17",
        },
    )

    assert response.status_code == 404
    assert not ScheduleRule.objects.filter(task=task).exists()
    assert not TaskOccurrence.objects.filter(task=task).exists()


@pytest.mark.django_db
def test_assignment_completion_rejects_mismatched_occurrence_in_url(client):
    user = get_user_model().objects.create_user(
        username="completion-scope-user",
        email="completion-scope@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Escopo da conclusão", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa com ocorrências distintas",
        created_by=user,
    )
    assigned_occurrence = TaskOccurrence.objects.create(
        task=task,
        scheduled_date=date(2026, 11, 17),
    )
    unrelated_occurrence = TaskOccurrence.objects.create(
        task=task,
        scheduled_date=date(2026, 11, 18),
    )
    assignment = assigned_occurrence.assignments.create(user=user)
    TaskExecution.objects.create(
        assignment=assignment,
        created_by=user,
        comments="Execução registrada antes da conclusão.",
    )
    client.force_login(user)

    response = client.post(
        reverse(
            "scheduling:complete-assignment",
            args=[workspace.pk, unrelated_occurrence.pk, assignment.pk],
        )
    )

    assert response.status_code == 404
    assignment.refresh_from_db()
    assert assignment.status == TaskAssignment.Status.PENDING
