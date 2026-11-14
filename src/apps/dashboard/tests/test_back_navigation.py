import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.scheduling.models import TaskOccurrence
from apps.tasks.models import Task
from apps.workspaces.models import Workspace, WorkspaceMembership


@pytest.fixture
def navigation_context(db):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="navigation-owner",
        email="navigation-owner@example.com",
        password="Strong-password-123!",
    )
    member = user_model.objects.create_user(
        username="navigation-member",
        email="navigation-member@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Navigation workspace", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=member,
        role=WorkspaceMembership.Role.MANAGER,
    )
    task = Task.objects.create(
        workspace=workspace,
        title="Navigation task",
        created_by=owner,
    )
    occurrence = TaskOccurrence.objects.create(
        task=task,
        scheduled_date="2026-11-21",
    )
    return {
        "user": owner,
        "workspace": workspace,
        "task": task,
        "occurrence": occurrence,
    }


@pytest.mark.django_db
def test_back_icon_is_present_on_all_authenticated_screens(client, navigation_context):
    context = navigation_context
    client.force_login(context["user"])
    workspace_detail = reverse("workspaces:detail", kwargs={"pk": context["workspace"].pk})
    task_list = reverse("tasks:list", kwargs={"workspace_id": context["workspace"].pk})
    calendar = reverse("scheduling:calendar", kwargs={"workspace_id": context["workspace"].pk})
    urls_and_fallbacks = [
        (reverse("dashboard:home"), reverse("workspaces:list")),
        (reverse("workspaces:list"), reverse("dashboard:home")),
        (workspace_detail, reverse("workspaces:list")),
        (reverse("workspaces:create"), reverse("workspaces:list")),
        (task_list, workspace_detail),
        (reverse("tasks:create", kwargs={"workspace_id": context["workspace"].pk}), task_list),
        (calendar, workspace_detail),
        (
            reverse(
                "scheduling:create",
                kwargs={
                    "workspace_id": context["workspace"].pk,
                    "task_id": context["task"].pk,
                },
            ),
            calendar,
        ),
        (
            reverse(
                "scheduling:occurrence-detail",
                kwargs={
                    "workspace_id": context["workspace"].pk,
                    "pk": context["occurrence"].pk,
                },
            ),
            calendar,
        ),
    ]

    for url, fallback in urls_and_fallbacks:
        response = client.get(url)
        assert response.status_code == 200, url
        assert b'aria-label="Voltar"' in response.content, url
        assert b'title="Voltar"' in response.content, url
        assert f'data-back-fallback="{fallback}"'.encode() in response.content, url
        assert b"document.referrer" in response.content
        assert b"window.history.back()" in response.content


@pytest.mark.django_db
def test_back_icon_falls_back_to_internal_dashboard(client, navigation_context):
    client.force_login(navigation_context["user"])

    response = client.get(reverse("workspaces:list"))

    assert response.status_code == 200
    assert f'data-back-fallback="{reverse("dashboard:home")}"'.encode() in response.content


@pytest.mark.django_db
def test_back_icon_does_not_use_external_referrer(client, navigation_context):
    client.force_login(navigation_context["user"])

    response = client.get(
        reverse("workspaces:list"),
        HTTP_REFERER="https://outside.example/path",
    )

    assert response.status_code == 200
    assert (
        f'data-back-fallback="{reverse("dashboard:home")}"'.encode()
        in response.content
    )
