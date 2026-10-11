import uuid

from django.conf import settings
from django.db import models


class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_workspaces",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def is_owner(self, user):
        if user is None:
            return False
        return getattr(user, "is_authenticated", False) and self.owner_id == user.pk

    def can_view(self, user):
        if user is None or not getattr(user, "is_authenticated", False):
            return False
        if self.is_owner(user):
            return True
        return self.memberships.filter(user=user, is_active=True).exists()

    def can_manage_space(self, user):
        if user is None or not getattr(user, "is_authenticated", False):
            return False
        if self.is_owner(user):
            return True
        return self.memberships.filter(
            user=user,
            is_active=True,
            role=WorkspaceMembership.Role.MANAGER,
        ).exists()

    def can_create_tasks(self, user):
        if user is None or not getattr(user, "is_authenticated", False):
            return False
        if self.is_owner(user):
            return True
        return self.memberships.filter(
            user=user,
            is_active=True,
            role__in=[
                WorkspaceMembership.Role.MANAGER,
                WorkspaceMembership.Role.COLLABORATOR,
            ],
        ).exists()

    def __str__(self):
        return self.name


class WorkspaceMembership(models.Model):
    class Role(models.TextChoices):
        MANAGER = "manager", "Gestor"
        COLLABORATOR = "collaborator", "Colaborador"
        READER = "reader", "Leitor"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="workspace_memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "user"],
                name="unique_workspace_user",
            )
        ]

    def can_view(self):
        return self.is_active and self.role in {
            self.Role.MANAGER,
            self.Role.COLLABORATOR,
            self.Role.READER,
        }

    def can_manage_space(self):
        return self.is_active and (
            self.role == self.Role.MANAGER or self.workspace.owner_id == self.user_id
        )

    def can_create_tasks(self):
        return self.is_active and self.role in {
            self.Role.MANAGER,
            self.Role.COLLABORATOR,
        }

    def __str__(self):
        return f"{self.user} em {self.workspace}"
