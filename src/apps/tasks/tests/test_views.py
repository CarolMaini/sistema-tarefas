from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.scheduling.models import TaskOccurrence
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "allowed"),
    [
        (None, True),
        ("manager", True),
        ("collaborator", False),
        ("reader", False),
    ],
)
def test_task_update_requires_owner_or_manager(client, role, allowed):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="task-update-owner",
        email="task-update-owner@example.com",
        password="Strong-password-123!",
    )
    actor = owner if role is None else user_model.objects.create_user(
        username=f"task-update-{role}",
        email=f"task-update-{role}@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Edição", owner=owner)
    if role:
        workspace.memberships.create(user=actor, role=role)
    task = Task.objects.create(
        workspace=workspace,
        title="Título original",
        description="Descrição original",
        created_by=owner,
    )
    client.force_login(actor)

    response = client.post(
        reverse("tasks:update", kwargs={"workspace_id": workspace.pk, "task_id": task.pk}),
        {"title": "Título atualizado", "description": "Descrição atualizada"},
    )

    if allowed:
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.title == "Título atualizado"
        assert task.description == "Descrição atualizada"
    else:
        assert response.status_code == 404
        task.refresh_from_db()
        assert task.title == "Título original"


@pytest.mark.django_db
def test_task_update_cannot_cross_workspace_boundary(client):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="task-boundary-owner",
        email="task-boundary-owner@example.com",
        password="Strong-password-123!",
    )
    other_owner = user_model.objects.create_user(
        username="task-boundary-other",
        email="task-boundary-other@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Workspace autorizado", owner=owner)
    other_workspace = Workspace.objects.create(name="Workspace alheio", owner=other_owner)
    task = Task.objects.create(
        workspace=other_workspace,
        title="Não alterar",
        created_by=other_owner,
    )
    client.force_login(owner)

    response = client.post(
        reverse("tasks:update", kwargs={"workspace_id": workspace.pk, "task_id": task.pk}),
        {"title": "Alteração indevida", "description": ""},
    )

    assert response.status_code == 404
    task.refresh_from_db()
    assert task.title == "Não alterar"


@pytest.mark.django_db
def test_owner_can_archive_task_without_deleting_history(client):
    user = get_user_model().objects.create_user(
        username="task-archive-owner",
        email="task-archive-owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Arquivamento", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa histórica",
        created_by=user,
    )
    client.force_login(user)

    response = client.post(
        reverse("tasks:archive", kwargs={"workspace_id": workspace.pk, "task_id": task.pk})
    )

    assert response.status_code == 302
    task.refresh_from_db()
    assert task.status == Task.Status.ARCHIVED
    assert Task.objects.filter(pk=task.pk).exists()


@pytest.mark.django_db
def test_collaborator_cannot_archive_task(client):
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="task-archive-owner-2",
        email="task-archive-owner-2@example.com",
        password="Strong-password-123!",
    )
    collaborator = user_model.objects.create_user(
        username="task-archive-collaborator",
        email="task-archive-collaborator@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Proteção de arquivamento", owner=owner)
    workspace.memberships.create(user=collaborator, role="collaborator")
    task = Task.objects.create(workspace=workspace, title="Preservar", created_by=owner)
    client.force_login(collaborator)

    response = client.post(
        reverse("tasks:archive", kwargs={"workspace_id": workspace.pk, "task_id": task.pk})
    )

    assert response.status_code == 404
    task.refresh_from_db()
    assert task.status == Task.Status.ACTIVE


@pytest.mark.django_db
def test_archived_task_cannot_be_edited(client):
    user = get_user_model().objects.create_user(
        username="task-archived-edit-owner",
        email="task-archived-edit-owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Tarefa arquivada", owner=user)
    task = Task.objects.create(
        workspace=workspace,
        title="Arquivada",
        created_by=user,
        status=Task.Status.ARCHIVED,
    )
    client.force_login(user)

    response = client.get(
        reverse("tasks:update", kwargs={"workspace_id": workspace.pk, "task_id": task.pk})
    )

    assert response.status_code == 404


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


@pytest.mark.django_db
def test_task_list_prefetches_only_three_upcoming_occurrences_per_task(client, monkeypatch):
    user = get_user_model().objects.create_user(
        username="task-list-prefetch-owner",
        email="task-list-prefetch-owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Listagem otimizada", owner=user)
    reference_date = date(2026, 11, 17)
    monkeypatch.setattr("apps.tasks.views.timezone.localdate", lambda: reference_date)

    tasks = [
        Task.objects.create(
            workspace=workspace,
            title=f"Tarefa {index}",
            created_by=user,
        )
        for index in range(5)
    ]
    for task in tasks:
        for offset in [-1, 0, 1, 2, 3, 4]:
            TaskOccurrence.objects.create(
                task=task,
                scheduled_date=reference_date + timedelta(days=offset),
            )

    client.force_login(user)
    url = reverse("tasks:list", kwargs={"workspace_id": workspace.pk})

    with CaptureQueriesContext(connection) as captured_queries:
        response = client.get(url)

    occurrence_queries = [
        query for query in captured_queries.captured_queries
        if "scheduling_taskoccurrence" in query["sql"].lower()
    ]

    assert response.status_code == 200
    assert len(occurrence_queries) == 1

    listed_tasks = list(response.context["tasks"])
    assert len(listed_tasks) == 5
    for task in listed_tasks:
        assert [item.scheduled_date for item in task.upcoming_occurrences] == [
            reference_date,
            reference_date + timedelta(days=1),
            reference_date + timedelta(days=2),
        ]


@pytest.mark.django_db
def test_task_list_paginates_ten_tasks_and_preserves_occurrence_prefetch(client):
    user = get_user_model().objects.create_user(
        username="task-list-pagination-owner",
        email="task-list-pagination-owner@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Paginação", owner=user)
    tasks = [
        Task.objects.create(
            workspace=workspace,
            title=f"Tarefa paginada {index:02d}",
            created_by=user,
        )
        for index in range(12)
    ]
    client.force_login(user)

    first_page = client.get(reverse("tasks:list", kwargs={"workspace_id": workspace.pk}))
    second_page = client.get(
        reverse("tasks:list", kwargs={"workspace_id": workspace.pk}),
        {"page": 2},
    )

    assert first_page.status_code == 200
    assert second_page.status_code == 200
    assert first_page.context["page_obj"].paginator.per_page == 10
    assert len(first_page.context["tasks"]) == 10
    assert len(second_page.context["tasks"]) == 2
    assert first_page.context["page_obj"].has_next()
    assert second_page.context["page_obj"].has_previous()
    assert second_page.context["tasks"][0].pk == tasks[1].pk
    assert "upcoming_occurrences" in second_page.context["tasks"][0].__dict__
