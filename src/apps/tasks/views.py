from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.audit.models import AuditEvent
from apps.scheduling.models import TaskOccurrence
from apps.workspaces.models import Workspace

from .models import Task


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.workspace = Workspace.objects.filter(pk=kwargs["workspace_id"]).first()
        if self.workspace is None or not self.workspace.can_view(request.user):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        upcoming_occurrences = (
            TaskOccurrence.objects.filter(scheduled_date__gte=timezone.localdate())
            .order_by("scheduled_date")[:3]
        )
        return (
            self.workspace.tasks.select_related("created_by")
            .prefetch_related(
                Prefetch(
                    "occurrences",
                    queryset=upcoming_occurrences,
                    to_attr="upcoming_occurrences",
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workspace"] = self.workspace
        context["can_create_tasks"] = self.workspace.can_create_tasks(self.request.user)
        context["can_manage_tasks"] = self.workspace.can_manage_space(self.request.user)
        return context


class TaskAuditHistoryView(LoginRequiredMixin, View):
    template_name = "tasks/task_audit_history.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.workspace = Workspace.objects.filter(pk=kwargs["workspace_id"]).first()
        if self.workspace is None or not self.workspace.can_view(request.user):
            raise Http404

        self.task = self.workspace.tasks.filter(pk=kwargs["task_id"]).first()
        if self.task is None:
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        events = (
            AuditEvent.objects.filter(workspace=self.workspace, task=self.task)
            .select_related("actor", "target_user", "assignment", "execution")
            .order_by("-created_at", "-pk")
        )
        page_obj = Paginator(events, 20).get_page(request.GET.get("page"))
        return render(
            request,
            self.template_name,
            {
                "workspace": self.workspace,
                "task": self.task,
                "events": page_obj.object_list,
                "page_obj": page_obj,
            },
        )


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ["title", "description"]
    template_name = "tasks/task_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.workspace = Workspace.objects.filter(pk=kwargs["workspace_id"]).first()
        if self.workspace is None or not self.workspace.can_create_tasks(request.user):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.workspace = self.workspace
        form.instance.created_by = self.request.user
        with transaction.atomic():
            response = super().form_valid(form)
            AuditEvent.objects.create(
                actor=self.request.user,
                workspace=self.workspace,
                task=self.object,
                action=AuditEvent.Action.TASK_CREATED,
            )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workspace"] = self.workspace
        return context

    def get_success_url(self):
        return reverse("tasks:list", kwargs={"workspace_id": self.workspace.pk})


class TaskManagementMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.workspace = Workspace.objects.filter(pk=kwargs["workspace_id"]).first()
        if self.workspace is None or not self.workspace.can_manage_space(request.user):
            raise Http404

        self.task = self.workspace.tasks.filter(pk=kwargs["task_id"]).first()
        if self.task is None:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("tasks:list", kwargs={"workspace_id": self.workspace.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workspace"] = self.workspace
        return context


class TaskUpdateView(TaskManagementMixin, LoginRequiredMixin, UpdateView):
    model = Task
    fields = ["title", "description"]
    template_name = "tasks/task_form.html"
    pk_url_kwarg = "task_id"

    def get_queryset(self):
        return self.workspace.tasks.filter(status=Task.Status.ACTIVE)

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            AuditEvent.objects.create(
                actor=self.request.user,
                workspace=self.workspace,
                task=self.object,
                action=AuditEvent.Action.TASK_UPDATED,
            )
        return response


class TaskArchiveView(TaskManagementMixin, LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if self.task.status != Task.Status.ARCHIVED:
            with transaction.atomic():
                self.task.status = Task.Status.ARCHIVED
                self.task.save(update_fields=["status", "updated_at"])
                AuditEvent.objects.create(
                    actor=request.user,
                    workspace=self.workspace,
                    task=self.task,
                    action=AuditEvent.Action.TASK_ARCHIVED,
                )
        return redirect(self.get_success_url())


__all__ = [
    "TaskListView",
    "TaskAuditHistoryView",
    "TaskCreateView",
    "TaskUpdateView",
    "TaskArchiveView",
]
