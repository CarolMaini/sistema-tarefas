from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView, ListView, View

from apps.audit.models import AuditEvent

from .forms import WorkspaceMemberForm
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
        context["memberships"] = workspace.memberships.filter(is_active=True).select_related("user")
        context["can_manage_space"] = workspace.can_manage_space(self.request.user)
        if context["can_manage_space"]:
            member_form = WorkspaceMemberForm(workspace=workspace)
            context["member_form"] = member_form
            context["has_available_members"] = member_form.fields["member"].queryset.exists()
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


class WorkspaceMemberAddView(LoginRequiredMixin, FormView):
    form_class = WorkspaceMemberForm
    http_method_names = ["post", "options"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.workspace = get_object_or_404(Workspace, pk=kwargs["pk"])
            if not self.workspace.can_manage_space(request.user):
                raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["workspace"] = self.workspace
        return kwargs

    def form_valid(self, form):
        member = form.cleaned_data["member"]
        with transaction.atomic():
            _, created = WorkspaceMembership.objects.get_or_create(
                workspace=self.workspace,
                user=member,
                defaults={
                    "role": WorkspaceMembership.Role.COLLABORATOR,
                    "is_active": True,
                },
            )
            if created:
                AuditEvent.objects.create(
                    actor=self.request.user,
                    workspace=self.workspace,
                    target_user=member,
                    action=AuditEvent.Action.WORKSPACE_MEMBER_ADDED,
                )

        if created:
            messages.success(self.request, "Membro adicionado ao workspace.")
        else:
            messages.info(self.request, "Essa pessoa já tem acesso a este workspace.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        error = next(iter(form.errors.values()))[0]
        messages.error(self.request, str(error))
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("workspaces:detail", kwargs={"pk": self.workspace.pk})


class WorkspaceMemberRemoveView(LoginRequiredMixin, View):
    http_method_names = ["post", "options"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.workspace = get_object_or_404(Workspace, pk=kwargs["pk"])
            if not self.workspace.can_manage_space(request.user):
                raise Http404
            self.membership = get_object_or_404(
                WorkspaceMembership,
                pk=kwargs["membership_id"],
                workspace=self.workspace,
                is_active=True,
            )
            if self.membership.user_id == self.workspace.owner_id:
                raise Http404
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            self.membership.is_active = False
            self.membership.save(update_fields=["is_active"])
            AuditEvent.objects.create(
                actor=request.user,
                workspace=self.workspace,
                target_user=self.membership.user,
                action=AuditEvent.Action.WORKSPACE_MEMBER_REMOVED,
            )

        messages.success(request, "Membro removido do workspace.")
        if self.membership.user_id == request.user.pk:
            return redirect("workspaces:list")
        return redirect("workspaces:detail", pk=self.workspace.pk)


__all__ = [
    "WorkspaceListView",
    "WorkspaceDetailView",
    "WorkspaceCreateView",
    "WorkspaceMemberAddView",
    "WorkspaceMemberRemoveView",
]
