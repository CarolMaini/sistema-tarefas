import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Ativa"
        ARCHIVED = "archived", "Arquivada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.PROTECT,
        related_name="tasks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_tasks",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class TaskAssignment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        COMPLETED = "completed", "Concluída"
        CANCELLED = "cancelled", "Cancelada"

    occurrence = models.ForeignKey(
        "scheduling.TaskOccurrence",
        on_delete=models.PROTECT,
        related_name="assignments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="task_assignments",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="completed_task_assignments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["occurrence", "user"],
                name="unique_occurrence_user",
            )
        ]

    def mark_completed(self, actor):
        if self.user_id != getattr(actor, "pk", None):
            raise ValueError("Only the assignee can complete this task assignment.")

        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.completed_by = actor
        self.save(update_fields=["status", "completed_at", "completed_by"])

    def __str__(self):
        return f"{self.user} -> {self.occurrence}"
