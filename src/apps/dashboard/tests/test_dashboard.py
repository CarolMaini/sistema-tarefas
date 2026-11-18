from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.scheduling.models import TaskOccurrence
from apps.tasks.models import Task, TaskAssignment
from apps.workspaces.models import Workspace, WorkspaceMembership


@pytest.fixture
def dashboard_context(db, monkeypatch):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="dashboard-user",
        email="dashboard-user@example.com",
        password="Strong-password-123!",
    )
    today = date(2026, 11, 17)
    monkeypatch.setattr("apps.dashboard.views.timezone.localdate", lambda: today)
    workspace = Workspace.objects.create(name="Meu espaço", owner=user)

    def create_assignment(
        title,
        scheduled_date,
        *,
        status=TaskAssignment.Status.PENDING,
        occurrence_status=TaskOccurrence.Status.OPEN,
        target_workspace=None,
        assignee=None,
    ):
        target_workspace = target_workspace or workspace
        task = Task.objects.create(
            workspace=target_workspace,
            title=title,
            created_by=target_workspace.owner,
        )
        occurrence = TaskOccurrence.objects.create(
            task=task,
            scheduled_date=scheduled_date,
            status=occurrence_status,
        )
        return TaskAssignment.objects.create(
            occurrence=occurrence,
            user=assignee or user,
            status=status,
        )

    return {
        "user": user,
        "workspace": workspace,
        "today": today,
        "create_assignment": create_assignment,
    }


@pytest.mark.django_db
def test_dashboard_requires_authentication(client):
    response = client.get(reverse("dashboard:home"))

    assert response.status_code == 302
    assert "/accounts/login" in response.url


@pytest.mark.django_db
def test_dashboard_counts_only_current_users_pending_assignments(
    client, dashboard_context
):
    context = dashboard_context
    create = context["create_assignment"]
    create("Pendente", context["today"])
    create("Concluída", context["today"], status=TaskAssignment.Status.COMPLETED)
    create("Cancelada", context["today"], status=TaskAssignment.Status.CANCELLED)

    other_user = get_user_model().objects.create_user(
        username="another-assignee",
        email="another-assignee@example.com",
        password="Strong-password-123!",
    )
    create("De outra pessoa", context["today"], assignee=other_user)

    client.force_login(context["user"])
    response = client.get(reverse("dashboard:home"))

    assert response.status_code == 200
    assert response.context["pending_tasks"] == 1


@pytest.mark.django_db
def test_dashboard_excludes_inaccessible_and_inactive_workspaces(
    client, dashboard_context
):
    context = dashboard_context
    outsider = get_user_model().objects.create_user(
        username="outsider",
        email="outsider@example.com",
        password="Strong-password-123!",
    )
    foreign_workspace = Workspace.objects.create(name="Alheio", owner=outsider)
    inactive_membership_workspace = Workspace.objects.create(
        name="Membro inativo", owner=outsider
    )
    WorkspaceMembership.objects.create(
        workspace=inactive_membership_workspace,
        user=context["user"],
        role=WorkspaceMembership.Role.MANAGER,
        is_active=False,
    )
    inactive_workspace = Workspace.objects.create(
        name="Espaço inativo", owner=context["user"], is_active=False
    )

    context["create_assignment"]("Visível", context["today"])
    context["create_assignment"](
        "Alheia", context["today"], target_workspace=foreign_workspace
    )
    context["create_assignment"](
        "Membership inativa",
        context["today"],
        target_workspace=inactive_membership_workspace,
    )
    context["create_assignment"](
        "Workspace inativo", context["today"], target_workspace=inactive_workspace
    )

    client.force_login(context["user"])
    response = client.get(reverse("dashboard:home"))

    assert response.context["pending_tasks"] == 1
    page = response.content.decode()
    assert "Alheia" not in page
    assert "Membership inativa" not in page
    assert "Workspace inativo" not in page


@pytest.mark.django_db
def test_dashboard_counts_open_pending_occurrences_in_inclusive_seven_day_window(
    client, dashboard_context
):
    context = dashboard_context
    create = context["create_assignment"]
    create("Hoje", context["today"])
    create("Último dia", context["today"] + timedelta(days=7))
    create("Ontem", context["today"] - timedelta(days=1))
    create("Depois da janela", context["today"] + timedelta(days=8))
    create(
        "Ocorrência cancelada",
        context["today"] + timedelta(days=1),
        occurrence_status=TaskOccurrence.Status.CANCELLED,
    )
    create(
        "Atribuição concluída",
        context["today"] + timedelta(days=1),
        status=TaskAssignment.Status.COMPLETED,
    )

    client.force_login(context["user"])
    response = client.get(reverse("dashboard:home"))

    assert response.context["upcoming_occurrences"] == 2
    assert [
        item.occurrence.task.title for item in response.context["upcoming_assignments"]
    ] == ["Hoje", "Último dia"]


@pytest.mark.django_db
def test_dashboard_limits_upcoming_assignments_to_ten_and_orders_them(
    client, dashboard_context
):
    context = dashboard_context
    create = context["create_assignment"]
    for index in range(12):
        create(
            f"Tarefa {index:02d}",
            context["today"] + timedelta(days=1 if index < 6 else 2),
        )

    client.force_login(context["user"])
    response = client.get(reverse("dashboard:home"))

    assignments = response.context["upcoming_assignments"]
    assert len(assignments) == 10
    assert [item.occurrence.task.title for item in assignments] == [
        f"Tarefa {index:02d}" for index in range(10)
    ]


@pytest.mark.django_db
def test_dashboard_links_to_the_correct_occurrence(client, dashboard_context):
    context = dashboard_context
    assignment = context["create_assignment"]("Abrir tarefa", context["today"])
    client.force_login(context["user"])

    response = client.get(reverse("dashboard:home"))
    expected_url = reverse(
        "scheduling:occurrence-detail",
        kwargs={
            "workspace_id": context["workspace"].pk,
            "pk": assignment.occurrence_id,
        },
    )

    assert response.status_code == 200
    assert expected_url.encode() in response.content


@pytest.mark.django_db
def test_dashboard_renders_distinct_empty_states(client, dashboard_context):
    context = dashboard_context
    client.force_login(context["user"])

    context["workspace"].delete()
    response_without_workspace = client.get(reverse("dashboard:home"))
    assert (
        "Você ainda não participa de nenhum espaço."
        in response_without_workspace.content.decode()
    )

    Workspace.objects.create(name="Espaço vazio", owner=context["user"])
    response_without_assignments = client.get(reverse("dashboard:home"))

    page = response_without_assignments.content.decode()
    assert "Nenhuma tarefa pendente no momento." in page
    assert "Não há próximas ações para os próximos 7 dias." in page
