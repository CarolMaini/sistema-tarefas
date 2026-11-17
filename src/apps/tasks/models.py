import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from PIL import Image, UnidentifiedImageError

MAX_EXECUTION_ATTACHMENT_SIZE = 10 * 1024 * 1024


def execution_attachment_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"task-executions/{uuid.uuid4().hex}{extension}"


def validate_execution_attachment(upload):
    if upload.size > MAX_EXECUTION_ATTACHMENT_SIZE:
        raise ValidationError("O anexo deve ter no máximo 10 MB.")

    extension = Path(upload.name).suffix.lower()
    if extension == ".pdf":
        if not upload.read(5).startswith(b"%PDF-"):
            raise ValidationError("O arquivo enviado não é um PDF válido.")
    elif extension in {".jpg", ".jpeg", ".png"}:
        try:
            image = Image.open(upload)
            expected_format = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG"}[extension]
            if image.format != expected_format:
                raise ValidationError("A extensão do arquivo não corresponde à imagem enviada.")
            image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise ValidationError("O arquivo enviado não é uma imagem válida.") from exc
    else:
        raise ValidationError("Envie uma imagem JPG/PNG ou um arquivo PDF.")

    upload.seek(0)


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

        if not self.executions.exists():
            raise ValueError("A task assignment requires an execution record before completion.")

        completed_at = timezone.now()
        updated = type(self).objects.filter(
            pk=self.pk,
            status=self.Status.PENDING,
        ).update(
            status=self.Status.COMPLETED,
            completed_at=completed_at,
            completed_by=actor,
        )
        if not updated:
            raise ValueError("Only pending task assignments can be completed.")

        self.status = self.Status.COMPLETED
        self.completed_at = completed_at
        self.completed_by = actor

    def __str__(self):
        return f"{self.user} -> {self.occurrence}"


class TaskExecution(models.Model):
    assignment = models.ForeignKey(
        TaskAssignment,
        on_delete=models.PROTECT,
        related_name="executions",
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to=execution_attachment_path,
        blank=True,
        validators=[validate_execution_attachment],
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="task_executions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        super().clean()
        if self.assignment_id and self.created_by_id:
            if self.assignment.user_id != self.created_by_id:
                raise ValidationError(
                    {
                        "created_by": (
                            "O registro de execução deve ser feito pelo responsável pela atribuição."
                        )
                    }
                )
        if self.started_at and self.ended_at and self.ended_at < self.started_at:
            raise ValidationError({"ended_at": "O horário de fim deve ser posterior ao início."})

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Execução de {self.assignment} em {self.created_at}"
