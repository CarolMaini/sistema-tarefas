import pytest
from django.contrib.auth import get_user_model

from apps.scheduling.forms import ScheduleRuleForm
from apps.scheduling.models import TaskOccurrence
from apps.scheduling.services import assign_occurrence
from apps.tasks.models import Task
from apps.workspaces.models import Workspace, WorkspaceMembership


def create_user(username, *, is_active=True):
    return get_user_model().objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="Strong-password-123!",
        is_active=is_active,
    )


@pytest.mark.django_db
def test_inactive_account_with_active_membership_is_not_assignable():
    owner = create_user("active-owner")
    inactive_member = create_user("inactive-member", is_active=False)
    workspace = Workspace.objects.create(name="Workspace", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=inactive_member,
        role=WorkspaceMembership.Role.COLLABORATOR,
        is_active=True,
    )

    assert workspace.can_assign_user(inactive_member) is False
    assert inactive_member not in workspace.get_assignable_users()
    assert inactive_member not in ScheduleRuleForm(workspace=workspace).fields[
        "default_assignee"
    ].queryset


@pytest.mark.django_db
def test_inactive_workspace_owner_is_not_assignable():
    inactive_owner = create_user("inactive-owner", is_active=False)
    workspace = Workspace.objects.create(name="Workspace", owner=inactive_owner)

    assert workspace.can_assign_user(inactive_owner) is False
    assert inactive_owner not in workspace.get_assignable_users()


@pytest.mark.django_db
def test_assign_occurrence_rejects_inactive_member_even_with_active_membership():
    owner = create_user("assignment-owner")
    inactive_member = create_user("assignment-inactive", is_active=False)
    workspace = Workspace.objects.create(name="Workspace", owner=owner)
    WorkspaceMembership.objects.create(
        workspace=workspace,
        user=inactive_member,
        role=WorkspaceMembership.Role.COLLABORATOR,
        is_active=True,
    )
    task = Task.objects.create(
        workspace=workspace,
        title="Tarefa",
        created_by=owner,
    )
    occurrence = TaskOccurrence.objects.create(
        task=task,
        scheduled_date="2026-11-18",
    )

    with pytest.raises(ValueError, match="não é elegível"):
        assign_occurrence(occurrence, inactive_member)

    assert not occurrence.assignments.exists()
