from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    class Action(models.TextChoices):
        WORKSPACE_MEMBER_ADDED = "workspace_member_added", "Membro adicionado ao workspace"
        WORKSPACE_MEMBER_REMOVED = "workspace_member_removed", "Membro removido do workspace"
        TASK_CREATED = "task_created", "Tarefa criada"
        TASK_UPDATED = "task_updated", "Tarefa atualizada"
        TASK_ARCHIVED = "task_archived", "Tarefa arquivada"
        TASK_ASSIGNMENT_CREATED = "task_assignment_created", "Responsável atribuído"
        TASK_ASSIGNMENT_COMPLETED = "task_assignment_completed", "Atribuição concluída"
        TASK_EXECUTION_CREATED = "task_execution_created", "Execução registrada"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_events",
    )
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.PROTECT,
        related_name="audit_events",
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="membership_audit_events",
        null=True,
        blank=True,
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.PROTECT,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    assignment = models.ForeignKey(
        "tasks.TaskAssignment",
        on_delete=models.PROTECT,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    execution = models.ForeignKey(
        "tasks.TaskExecution",
        on_delete=models.PROTECT,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=40, choices=Action.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]