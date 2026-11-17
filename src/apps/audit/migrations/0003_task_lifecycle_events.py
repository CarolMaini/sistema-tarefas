import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0002_alter_auditevent_action"),
        ("tasks", "0002_taskexecution"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditevent",
            name="target_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="membership_audit_events",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="auditevent",
            name="task",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="audit_events",
                to="tasks.task",
            ),
        ),
        migrations.AddField(
            model_name="auditevent",
            name="assignment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="audit_events",
                to="tasks.taskassignment",
            ),
        ),
        migrations.AddField(
            model_name="auditevent",
            name="execution",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="audit_events",
                to="tasks.taskexecution",
            ),
        ),
        migrations.AlterField(
            model_name="auditevent",
            name="action",
            field=models.CharField(
                choices=[
                    ("workspace_member_added", "Membro adicionado ao workspace"),
                    ("workspace_member_removed", "Membro removido do workspace"),
                    ("task_created", "Tarefa criada"),
                    ("task_updated", "Tarefa atualizada"),
                    ("task_archived", "Tarefa arquivada"),
                    ("task_assignment_created", "Responsável atribuído"),
                    ("task_assignment_completed", "Atribuição concluída"),
                    ("task_execution_created", "Execução registrada"),
                ],
                max_length=40,
            ),
        ),
    ]
