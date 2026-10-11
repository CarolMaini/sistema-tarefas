import uuid

from django.conf import settings
from django.db import models


class ScheduleRule(models.Model):
    class Frequency(models.TextChoices):
        WEEKLY = "weekly", "Semanal"
        BIWEEKLY = "biweekly", "Quinzenal"
        MONTHLY = "monthly", "Mensal"

    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.PROTECT,
        related_name="schedule_rules",
    )
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.WEEKLY,
    )
    starts_on = models.DateField()
    anchor_date = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    weekdays = models.JSONField(default=list)
    timezone = models.CharField(max_length=64, default="America/Sao_Paulo")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_schedule_rules",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Regra de recorrência para {self.task}"


class TaskOccurrence(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Aberta"
        CANCELLED = "cancelled", "Cancelada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.PROTECT,
        related_name="occurrences",
    )
    schedule_rule = models.ForeignKey(
        "scheduling.ScheduleRule",
        on_delete=models.PROTECT,
        related_name="occurrences",
        null=True,
        blank=True,
    )
    scheduled_date = models.DateField()
    starts_at = models.TimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["task", "scheduled_date"],
                name="unique_task_occurrence_date",
            )
        ]

    def __str__(self):
        return f"{self.task} em {self.scheduled_date}"
