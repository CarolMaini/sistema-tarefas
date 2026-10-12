from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.workspaces.models import Workspace


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        owned = Workspace.objects.filter(owner=user)
        member = Workspace.objects.filter(
            memberships__user=user,
            memberships__is_active=True,
        )
        workspaces = (owned | member).distinct().order_by("name")

        active_workspace = None
        workspace_id = self.kwargs.get("workspace_id")
        if workspace_id:
            active_workspace = Workspace.objects.filter(
                pk=workspace_id,
                is_active=True,
            ).first()

        if active_workspace is None and workspaces.exists():
            active_workspace = workspaces.first()

        context["workspaces"] = workspaces
        context["active_workspace"] = active_workspace
        context["pending_tasks"] = 0
        context["upcoming_occurrences"] = 0
        context["today"] = date.today()
        context["user_name"] = user.get_full_name() or user.username
        return context
