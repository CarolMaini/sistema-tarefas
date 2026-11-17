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


@pytest.mark.django_db
def test_owner_cannot_access_tasks_in_inactive_workspace(client):
    user = get_user_model().objects.create_user(
        username="inactive-task-owner",
        email="inactive-task-owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(
        name="Espaço desativado",
        owner=user,
        is_active=False,
    )
    client.force_login(user)

    list_response = client.get(reverse("tasks:list", kwargs={"workspace_id": workspace.pk}))
    create_response = client.get(reverse("tasks:create", kwargs={"workspace_id": workspace.pk}))

    assert list_response.status_code == 404
    assert create_response.status_code == 404


@pytest.mark.parametrize(
    ("actor_role", "is_owner", "membership_active", "expected_status"),
    [
        (None, True, True, 302),
        ("manager", False, True, 302),
        ("collaborator", False, True, 302),
        ("reader", False, True, 404),
        ("collaborator", False, False, 404),
        (None, False, True, 404),
    ],
)
@pytest.mark.django_db
def test_task_creation_enforces_workspace_role_permissions(
    client, actor_role, is_owner, membership_active, expected_status
):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="task-permission-owner",
        email="task-permission-owner@example.com",
        password="Strong-password-123!",
    )
    actor = owner if is_owner else user_model.objects.create_user(
        username=f"task-actor-{actor_role or 'outsider'}-{membership_active}",
        email=f"task-actor-{actor_role or 'outsider'}-{membership_active}@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Permissões de tarefas", owner=owner)
    if actor_role:
        workspace.memberships.create(
            user=actor,
            role=actor_role,
            is_active=membership_active,
        )
    client.force_login(actor)

    response = client.post(
        reverse("tasks:create", kwargs={"workspace_id": workspace.pk}),
        {"title": "Tarefa protegida", "description": "Teste de autorização."},
    )

    assert response.status_code == expected_status
    if expected_status == 302:
        task = Task.objects.get(workspace=workspace, title="Tarefa protegida")
        assert task.created_by == actor
    else:
        assert not Task.objects.filter(workspace=workspace).exists()
