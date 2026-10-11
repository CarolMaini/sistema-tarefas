import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.tasks.models import Task
from apps.workspaces.models import Workspace


@pytest.mark.django_db
def test_task_list_requires_login(client):
    user = get_user_model().objects.create_user(
        username="guest",
        email="guest@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Gestão", owner=user)

    response = client.get(reverse("tasks:list", kwargs={"workspace_id": workspace.pk}))

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


@pytest.mark.django_db
def test_owner_can_see_tasks_in_workspace(client):
    user = get_user_model().objects.create_user(
        username="owner",
        email="owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Operações", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Preparar relatório",
        description="Revisar métricas do mês.",
        created_by=user,
    )
    client.force_login(user)

    response = client.get(reverse("tasks:list", kwargs={"workspace_id": workspace.pk}))

    assert response.status_code == 200
    assert task.title.encode() in response.content
