from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from apps.scheduling.models import TaskOccurrence
from apps.tasks.models import TaskAssignment
from apps.workspaces.models import Workspace


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        owned = Workspace.objects.filter(owner=user, is_active=True)
        member = Workspace.objects.filter(
            memberships__user=user,
            memberships__is_active=True,
            is_active=True,
        )
        workspaces = (owned | member).distinct().order_by("name")

        active_workspace = None
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id:
            active_workspace = workspaces.filter(pk=workspace_id).first()

        if active_workspace is None and workspaces.exists():
            active_workspace = workspaces.first()

        today = timezone.localdate()
        pending_assignments = (
            TaskAssignment.objects.filter(
                user=user,
                status=TaskAssignment.Status.PENDING,
                occurrence__task__workspace__in=workspaces,
            )
            .select_related(
                "occurrence",
                "occurrence__task",
                "occurrence__task__workspace",
            )
        )
        upcoming_assignments = pending_assignments.filter(
            occurrence__status=TaskOccurrence.Status.OPEN,
            occurrence__scheduled_date__gte=today,
            occurrence__scheduled_date__lte=today + timedelta(days=7),
        ).order_by(
            "occurrence__scheduled_date",
            "occurrence__task__title",
        )

        context.update(
            {
                "workspaces": workspaces,
                "active_workspace": active_workspace,
                "pending_tasks": pending_assignments.count(),
                "upcoming_occurrences": upcoming_assignments.count(),
                "upcoming_assignments": upcoming_assignments[:10],
                "today": today,
                "user_name": user.get_full_name() or user.username,
            }
        )
        return context
