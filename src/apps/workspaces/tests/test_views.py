import pytest
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse

from apps.audit.models import AuditEvent
from apps.workspaces.models import Workspace, WorkspaceMembership


@pytest.mark.django_db
def test_workspace_list_requires_login(client):
    response = client.get(reverse("workspaces:list"))

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


@pytest.mark.django_db
def test_manager_can_create_workspace(client):
    user = get_user_model().objects.create_user(
        username="manager",
        email="manager@example.com",
        password="Strong-password-123!",
    )
    client.force_login(user)

    response = client.post(
        reverse("workspaces:create"),
        {
            "name": "Equipe Financeira",
            "description": "Planejamento do mês.",
        },
    )

    assert response.status_code == 302
    assert Workspace.objects.filter(name="Equipe Financeira", owner=user).exists()


def create_user(username, email, *, is_active=True):
    return get_user_model().objects.create_user(
        username=username,
        email=email,
        password="Strong-password-123!",
        is_active=is_active,
    )


def add_member_url(workspace):
    return reverse("workspaces:member-add", kwargs={"pk": workspace.pk})


def remove_member_url(workspace, membership):
    return reverse(
        "workspaces:member-remove",
        kwargs={"pk": workspace.pk, "membership_id": membership.pk},
    )


@pytest.mark.django_db
def test_owner_can_add_active_account_and_audit_membership(client):
    owner = create_user("owner-add", "owner-add@example.com")
    target = create_user("target-add", "target-add@example.com")
    workspace = Workspace.objects.create(name="Workspace owner", owner=owner)
    client.force_login(owner)

    response = client.post(add_member_url(workspace), {"member": target.pk})

    membership = WorkspaceMembership.objects.get(workspace=workspace, user=target)
    event = AuditEvent.objects.get(workspace=workspace, target_user=target)
    assert response.status_code == 302
    assert membership.role == WorkspaceMembership.Role.COLLABORATOR
    assert membership.is_active is True
    assert event.actor == owner
    assert event.action == AuditEvent.Action.WORKSPACE_MEMBER_ADDED


@pytest.mark.django_db
def test_manager_can_add_active_account(client):
    owner = create_user("owner-manager", "owner-manager@example.com")
    manager = create_user("manager-add", "manager-add@example.com")
    target = create_user("target-manager", "target-manager@example.com")
    workspace = Workspace.objects.create(name="Workspace manager", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=manager,
        role=WorkspaceMembership.Role.MANAGER,
    )
    client.force_login(manager)

    response = client.post(add_member_url(workspace), {"member": target.pk})

    assert response.status_code == 302
    assert WorkspaceMembership.objects.filter(
        workspace=workspace,
        user=target,
        role=WorkspaceMembership.Role.COLLABORATOR,
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [WorkspaceMembership.Role.COLLABORATOR, WorkspaceMembership.Role.READER],
)
def test_non_manager_cannot_add_member(client, role):
    owner = create_user(f"owner-{role}", f"owner-{role}@example.com")
    actor = create_user(f"actor-{role}", f"actor-{role}@example.com")
    target = create_user(f"target-{role}", f"target-{role}@example.com")
    workspace = Workspace.objects.create(name=f"Workspace {role}", owner=owner)
    WorkspaceMembership.objects.create(workspace=workspace, user=actor, role=role)
    client.force_login(actor)

    response = client.post(add_member_url(workspace), {"email": target.email})

    assert response.status_code in {403, 404}
    assert not WorkspaceMembership.objects.filter(workspace=workspace, user=target).exists()
    assert not AuditEvent.objects.filter(workspace=workspace).exists()


@pytest.mark.django_db
def test_inactive_account_id_is_rejected(client):
    owner = create_user("owner-inactive", "owner-inactive@example.com")
    target = create_user("inactive-target", "inactive-target@example.com", is_active=False)
    workspace = Workspace.objects.create(name="Workspace inactive account", owner=owner)
    client.force_login(owner)

    response = client.post(add_member_url(workspace), {"member": target.pk}, follow=True)

    assert response.status_code == 200
    assert not WorkspaceMembership.objects.filter(workspace=workspace).exclude(user=owner).exists()
    assert not AuditEvent.objects.filter(workspace=workspace).exists()
    assert list(get_messages(response.wsgi_request))


@pytest.mark.django_db
@pytest.mark.parametrize("is_active", [True, False])
def test_existing_membership_is_not_duplicated_or_reactivated(client, is_active):
    owner = create_user(
        f"owner-duplicate-{is_active}",
        f"owner-duplicate-{is_active}@example.com",
    )
    target = create_user(
        f"target-duplicate-{is_active}",
        f"target-duplicate-{is_active}@example.com",
    )
    workspace = Workspace.objects.create(name="Workspace duplicate", owner=owner)
    existing = WorkspaceMembership.objects.create(
        workspace=workspace,
        user=target,
        role=WorkspaceMembership.Role.READER,
        is_active=is_active,
    )
    client.force_login(owner)

    response = client.post(add_member_url(workspace), {"member": target.pk}, follow=True)

    existing.refresh_from_db()
    assert response.status_code == 200
    assert WorkspaceMembership.objects.filter(workspace=workspace, user=target).count() == 1
    assert existing.is_active is is_active
    assert not AuditEvent.objects.filter(workspace=workspace, target_user=target).exists()
    assert list(get_messages(response.wsgi_request))


@pytest.mark.django_db
def test_owner_account_id_is_rejected(client):
    owner = create_user("owner-self", "owner-self@example.com")
    workspace = Workspace.objects.create(name="Workspace owner self", owner=owner)
    client.force_login(owner)

    response = client.post(add_member_url(workspace), {"member": owner.pk}, follow=True)

    assert response.status_code == 200
    assert WorkspaceMembership.objects.filter(workspace=workspace, user=owner).count() == 0
    assert not AuditEvent.objects.filter(workspace=workspace).exists()
    assert list(get_messages(response.wsgi_request))


@pytest.mark.django_db
def test_workspace_detail_lists_only_active_users_without_membership(client):
    owner = create_user("owner-options", "owner-options@example.com")
    candidate = create_user("candidate", "candidate@example.com")
    active_member = create_user("active-member", "active-member@example.com")
    inactive_member = create_user("inactive-member", "inactive-member@example.com")
    inactive_account = create_user(
        "inactive-account",
        "inactive-account@example.com",
        is_active=False,
    )
    workspace = Workspace.objects.create(name="Workspace choices", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=active_member,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=inactive_member,
        role=WorkspaceMembership.Role.READER,
        is_active=False,
    )
    client.force_login(owner)

    response = client.get(reverse("workspaces:detail", kwargs={"pk": workspace.pk}))

    assert response.status_code == 200
    assert f'value="{candidate.pk}"'.encode() in response.content
    assert f'value="{active_member.pk}"'.encode() not in response.content
    assert f'value="{inactive_member.pk}"'.encode() not in response.content
    assert f'value="{inactive_account.pk}"'.encode() not in response.content
    assert f'value="{owner.pk}"'.encode() not in response.content


@pytest.mark.django_db
def test_workspace_detail_shows_empty_state_when_no_users_are_available(client):
    owner = create_user("owner-no-options", "owner-no-options@example.com")
    workspace = Workspace.objects.create(name="Workspace without candidates", owner=owner)
    client.force_login(owner)

    response = client.get(reverse("workspaces:detail", kwargs={"pk": workspace.pk}))

    assert response.status_code == 200
    assert (
        b"N\xc3\xa3o h\xc3\xa1 usu\xc3\xa1rios ativos dispon\xc3\xadveis para adicionar."
        in response.content
    )
    assert b"<select" not in response.content
    assert b"Adicionar membro" not in response.content


@pytest.mark.django_db
def test_member_post_rejects_user_not_in_available_choices(client):
    owner = create_user("owner-forged", "owner-forged@example.com")
    target = create_user("existing-target", "existing-target@example.com")
    workspace = Workspace.objects.create(name="Workspace forged selection", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=target,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    client.force_login(owner)

    response = client.post(add_member_url(workspace), {"member": target.pk}, follow=True)

    assert response.status_code == 200
    assert WorkspaceMembership.objects.filter(workspace=workspace, user=target).count() == 1
    assert not AuditEvent.objects.filter(workspace=workspace, target_user=target).exists()
    assert list(get_messages(response.wsgi_request))


@pytest.mark.django_db
def test_workspace_detail_shows_member_form_only_to_managers(client):
    owner = create_user("owner-form", "owner-form@example.com")
    collaborator = create_user("collaborator-form", "collaborator-form@example.com")
    create_user("available-form", "available-form@example.com")
    workspace = Workspace.objects.create(name="Workspace member form", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=collaborator,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    detail_url = reverse("workspaces:detail", kwargs={"pk": workspace.pk})

    client.force_login(owner)
    owner_response = client.get(detail_url)
    client.force_login(collaborator)
    collaborator_response = client.get(detail_url)

    assert owner_response.status_code == 200
    assert b"Adicionar membro" in owner_response.content
    assert b"/members/add/" in owner_response.content
    assert collaborator_response.status_code == 200
    assert b"Adicionar membro" not in collaborator_response.content


@pytest.mark.django_db
def test_manager_can_remove_member_and_audit_deactivation(client):
    owner = create_user("owner-remove", "owner-remove@example.com")
    manager = create_user("manager-remove", "manager-remove@example.com")
    target = create_user("target-remove", "target-remove@example.com")
    workspace = Workspace.objects.create(name="Workspace remove", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=manager,
        role=WorkspaceMembership.Role.MANAGER,
    )
    membership = WorkspaceMembership.objects.create(
        workspace=workspace,
        user=target,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    client.force_login(manager)

    response = client.post(remove_member_url(workspace, membership))

    membership.refresh_from_db()
    event = AuditEvent.objects.get(
        workspace=workspace,
        target_user=target,
        action=AuditEvent.Action.WORKSPACE_MEMBER_REMOVED,
    )
    assert response.status_code == 302
    assert membership.is_active is False
    assert event.actor == manager
    assert not WorkspaceMembership.objects.filter(
        workspace=workspace,
        user=target,
        is_active=True,
    ).exists()


@pytest.mark.django_db
def test_collaborator_cannot_remove_member(client):
    owner = create_user("owner-remove-denied", "owner-remove-denied@example.com")
    collaborator = create_user("collab-remove", "collab-remove@example.com")
    target = create_user("target-remove-denied", "target-remove-denied@example.com")
    workspace = Workspace.objects.create(name="Workspace remove denied", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=collaborator,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    membership = WorkspaceMembership.objects.create(
        workspace=workspace,
        user=target,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    client.force_login(collaborator)

    response = client.post(remove_member_url(workspace, membership))

    membership.refresh_from_db()
    assert response.status_code == 404
    assert membership.is_active is True
    assert not AuditEvent.objects.filter(
        workspace=workspace,
        action=AuditEvent.Action.WORKSPACE_MEMBER_REMOVED,
    ).exists()


@pytest.mark.django_db
def test_manager_cannot_remove_workspace_owner(client):
    owner = create_user("owner-protected", "owner-protected@example.com")
    manager = create_user("manager-protected", "manager-protected@example.com")
    workspace = Workspace.objects.create(name="Protected owner", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=manager,
        role=WorkspaceMembership.Role.MANAGER,
    )
    owner_membership = WorkspaceMembership.objects.create(
        workspace=workspace,
        user=owner,
        role=WorkspaceMembership.Role.MANAGER,
    )
    client.force_login(manager)

    response = client.post(remove_member_url(workspace, owner_membership))

    owner_membership.refresh_from_db()
    assert response.status_code == 404
    assert owner_membership.is_active is True


@pytest.mark.django_db
def test_only_manager_sees_remove_member_action(client):
    owner = create_user("owner-remove-ui", "owner-remove-ui@example.com")
    manager = create_user("manager-remove-ui", "manager-remove-ui@example.com")
    collaborator = create_user("collab-remove-ui", "collab-remove-ui@example.com")
    target = create_user("target-remove-ui", "target-remove-ui@example.com")
    workspace = Workspace.objects.create(name="Workspace remove UI", owner=owner)
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
    target_membership = WorkspaceMembership.objects.create(
        workspace=workspace,
        user=target,
        role=WorkspaceMembership.Role.COLLABORATOR,
    )
    detail_url = reverse("workspaces:detail", kwargs={"pk": workspace.pk})

    client.force_login(manager)
    manager_response = client.get(detail_url)
    client.force_login(collaborator)
    collaborator_response = client.get(detail_url)

    remove_path = f"/members/{target_membership.pk}/remove/".encode()
    assert manager_response.status_code == 200
    assert remove_path in manager_response.content
    assert collaborator_response.status_code == 200
    assert remove_path not in collaborator_response.content


@pytest.mark.django_db
def test_inactive_workspace_is_hidden_and_owner_cannot_open_it(client):
    owner = create_user("inactive-space-owner", "inactive-space-owner@example.com")
    workspace = Workspace.objects.create(
        name="Espaço desativado",
        owner=owner,
        is_active=False,
    )
    client.force_login(owner)

    list_response = client.get(reverse("workspaces:list"))
    detail_response = client.get(reverse("workspaces:detail", kwargs={"pk": workspace.pk}))

    assert list_response.status_code == 200
    assert "Espaço desativado".encode() not in list_response.content
    assert detail_response.status_code == 404
