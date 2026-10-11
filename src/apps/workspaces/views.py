from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from .models import Workspace, WorkspaceMembership


class WorkspaceListView(LoginRequiredMixin, ListView):
    model = Workspace
    template_name = "workspaces/workspace_list.html"
    context_object_name = "workspaces"

    def get_queryset(self):
        user = self.request.user
        owned = Workspace.objects.filter(owner=user)
        member = Workspace.objects.filter(
            memberships__user=user,
            memberships__is_active=True,
        )
        return (owned | member).distinct().order_by("name")


class WorkspaceDetailView(LoginRequiredMixin, DetailView):
    model = Workspace
    template_name = "workspaces/workspace_detail.html"
    context_object_name = "workspace"

    def get_object(self, queryset=None):
        workspace = super().get_object(queryset)
        if not workspace.can_view(self.request.user):
            raise Http404
        return workspace

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workspace = self.object
        context["tasks"] = workspace.tasks.filter(status=workspace.tasks.model.Status.ACTIVE)
        context["memberships"] = workspace.memberships.select_related("user").all()
        return context


class WorkspaceCreateView(LoginRequiredMixin, CreateView):
    model = Workspace
    template_name = "workspaces/workspace_form.html"
    fields = ["name", "description"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        with transaction.atomic():
            response = super().form_valid(form)
            WorkspaceMembership.objects.create(
                workspace=self.object,
                user=self.request.user,
                role=WorkspaceMembership.Role.MANAGER,
            )
        messages.success(self.request, "Espaço criado com sucesso.")
        return response

    def get_success_url(self):
        return reverse("workspaces:detail", kwargs={"pk": self.object.pk})


__all__ = [
    "WorkspaceListView",
    "WorkspaceDetailView",
    "WorkspaceCreateView",
]
