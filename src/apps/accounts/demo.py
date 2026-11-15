from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from apps.scheduling.models import TaskOccurrence
from apps.tasks.models import Task, TaskAssignment
from apps.workspaces.models import Workspace, WorkspaceMembership

DEMO_EMAIL = "visitante@organizador.demo"
DEMO_USERNAME = "visitante-demo"


@require_POST
def demo_login(request):
    if not settings.DEMO_ACCESS_ENABLED:
        raise Http404

    user_model = get_user_model()
    with transaction.atomic():
        user, created = user_model.objects.get_or_create(
            email=DEMO_EMAIL,
            defaults={
                "username": DEMO_USERNAME,
                "first_name": "Visitante",
                "last_name": "Demonstração",
                "display_name": "Visitante",
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])

        workspace, _ = Workspace.objects.get_or_create(
            owner=user,
            name="Espaço de demonstração",
            defaults={
                "description": (
                    "Um espaço de exemplo para explorar tarefas, calendário e recorrências."
                ),
                "is_active": True,
            },
        )
        WorkspaceMembership.objects.get_or_create(
            workspace=workspace,
            user=user,
            defaults={
                "role": WorkspaceMembership.Role.MANAGER,
                "is_active": True,
            },
        )

        sample_tasks = [
            (
                "Planejar a semana",
                "Organize prioridades e distribua as atividades dos próximos dias.",
            ),
            (
                "Revisar atividades do projeto",
                "Acompanhe o andamento e registre os próximos passos.",
            ),
        ]
        for index, (title, description) in enumerate(sample_tasks):
            task, _ = Task.objects.get_or_create(
                workspace=workspace,
                title=title,
                defaults={
                    "description": description,
                    "created_by": user,
                    "status": Task.Status.ACTIVE,
                },
            )
            if index == 0:
                occurrence_date = timezone.localdate() + timedelta(days=1)
                occurrence, _ = TaskOccurrence.objects.get_or_create(
                    task=task,
                    scheduled_date=occurrence_date,
                    defaults={"status": TaskOccurrence.Status.OPEN},
                )
                TaskAssignment.objects.get_or_create(
                    occurrence=occurrence,
                    user=user,
                    defaults={"status": TaskAssignment.Status.PENDING},
                )

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    request.session["demo_access"] = True
    return redirect("dashboard:home")


@require_GET
def demo_logout(request):
    if not request.session.get("demo_access"):
        raise Http404

    logout(request)
    return redirect(reverse("account_login"))
