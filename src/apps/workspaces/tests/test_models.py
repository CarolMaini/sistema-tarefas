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


@pytest.mark.django_db
def test_assignable_users_are_distinct_and_require_owner_or_active_membership():
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="assignable-owner",
        email="assignable-owner@example.com",
        password="Strong-password-123!",
    )
    active_member = user_model.objects.create_user(
        username="assignable-member",
        email="assignable-member@example.com",
        password="Strong-password-123!",
    )
    inactive_member = user_model.objects.create_user(
        username="inactive-member",
        email="inactive-member@example.com",
        password="Strong-password-123!",
    )
    external_user = user_model.objects.create_user(
        username="external-user",
        email="external-user@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Elegibilidade", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=owner,
        role=WorkspaceMembership.Role.MANAGER,
    )
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=active_member,
        role=WorkspaceMembership.Role.READER,
    )
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=inactive_member,
        role=WorkspaceMembership.Role.COLLABORATOR,
        is_active=False,
    )

    assignable_ids = {user.pk for user in workspace.get_assignable_users()}

    assert assignable_ids == {owner.pk, active_member.pk}
    assert workspace.can_assign_user(owner) is True
    assert workspace.can_assign_user(active_member) is True
    assert workspace.can_assign_user(inactive_member) is False
    assert workspace.can_assign_user(external_user) is False


@pytest.mark.django_db
def test_inactive_workspace_denies_all_workspace_permissions():
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="inactive-workspace-owner",
        email="inactive-workspace-owner@example.com",
        password="Strong-password-123!",
    )
    member = user_model.objects.create_user(
        username="inactive-workspace-member",
        email="inactive-workspace-member@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(
        name="Espaço desativado",
        owner=owner,
        is_active=False,
    )
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=member,
        role=WorkspaceMembership.Role.MANAGER,
    )

    for user in (owner, member):
        assert workspace.can_view(user) is False
        assert workspace.can_manage_space(user) is False
        assert workspace.can_create_tasks(user) is False
        assert workspace.can_assign_user(user) is False

    assert not workspace.get_assignable_users().exists()


@pytest.mark.django_db
def test_deactivated_account_loses_all_workspace_permissions():
    user_model = get_user_model()
    owner = user_model.objects.create_user(
        username="deactivated-owner",
        email="deactivated-owner@example.com",
        password="Strong-password-123!",
    )
    manager = user_model.objects.create_user(
        username="deactivated-manager",
        email="deactivated-manager@example.com",
        password="Strong-password-123!",
    )
    collaborator = user_model.objects.create_user(
        username="deactivated-collaborator",
        email="deactivated-collaborator@example.com",
        password="Strong-password-123!",
    )
    workspace = Workspace.objects.create(name="Active workspace", owner=owner)
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

    for user in (owner, manager, collaborator):
        user.is_active = False
        user.save(update_fields=["is_active"])

        assert workspace.is_owner(user) is False
        assert workspace.can_view(user) is False
        assert workspace.can_manage_space(user) is False
        assert workspace.can_create_tasks(user) is False
        assert workspace.can_assign_user(user) is False
