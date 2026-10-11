import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.workspaces.models import Workspace, WorkspaceMembership


@pytest.mark.django_db
def test_workspace_owner_can_create_workspace_and_membership():
    user = get_user_model().objects.create_user(
        username="alice",
        email="alice@example.com",
        password="Strong-password-123!",
    )

    workspace = Workspace.objects.create(
        name="Equipe Marketing",
        description="Espaço de campanha e planejamento.",
        owner=user,
    )
    membership = WorkspaceMembership.objects.create(
        workspace=workspace,
        user=user,
        role=WorkspaceMembership.Role.MANAGER,
    )

    assert str(workspace) == "Equipe Marketing"
    assert workspace.owner == user
    assert workspace.memberships.count() == 1
    assert membership.is_active is True
    assert membership.role == WorkspaceMembership.Role.MANAGER


@pytest.mark.django_db
def test_duplicate_membership_is_rejected():
    user = get_user_model().objects.create_user(
        username="bob",
        email="bob@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(
        name="Equipe Operações",
        owner=user,
    )

    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=user,
        role=WorkspaceMembership.Role.MANAGER,
    )

    with pytest.raises(IntegrityError):
        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=user,
            role=WorkspaceMembership.Role.COLLABORATOR,
        )


@pytest.mark.django_db
def test_workspace_permission_boundaries_follow_role_matrix():
    owner = get_user_model().objects.create_user(
        username="owner",
        email="owner@example.com",
        password="Strong-password-123!",
    )
    manager = get_user_model().objects.create_user(
        username="manager",
        email="manager@example.com",
        password="Strong-password-123!",
    )
    collaborator = get_user_model().objects.create_user(
        username="collaborator",
        email="collaborator@example.com",
        password="Strong-password-123!",
    )
    reader = get_user_model().objects.create_user(
        username="reader",
        email="reader@example.com",
        password="Strong-password-123!",
    )

    workspace = Workspace.objects.create(name="Sprint Team", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=manager,
        role=WorkspaceMembership.Role.MANAGER,
    )
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=collaborator,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=reader,
        role=WorkspaceMembership.Role.READER,
    )

    assert workspace.can_view(owner) is True
    assert workspace.can_view(manager) is True
    assert workspace.can_view(collaborator) is True
    assert workspace.can_view(reader) is True

    assert workspace.can_manage_space(owner) is True
    assert workspace.can_manage_space(manager) is True
    assert workspace.can_manage_space(collaborator) is False
    assert workspace.can_manage_space(reader) is False

    assert workspace.can_create_tasks(owner) is True
    assert workspace.can_create_tasks(manager) is True
    assert workspace.can_create_tasks(collaborator) is True
    assert workspace.can_create_tasks(reader) is False

    inactive_membership = WorkspaceMembership.objects.create(
        workspace=workspace,
        user=get_user_model().objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="Strong-password-123!",
        ),
        role=WorkspaceMembership.Role.COLLABORATOR,
        is_active=False,
    )

    assert workspace.can_view(inactive_membership.user) is False
    assert inactive_membership.can_view() is False
