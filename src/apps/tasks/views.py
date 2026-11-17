from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

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
        return self.workspace.tasks.select_related("created_by").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workspace"] = self.workspace
        context["can_create_tasks"] = self.workspace.can_create_tasks(self.request.user)
        context["can_manage_tasks"] = self.workspace.can_manage_space(self.request.user)
        for task in context["tasks"]:
            task.upcoming_occurrences = task.occurrences.filter(
                scheduled_date__gte=date.today(),
            ).order_by("scheduled_date")[:3]
        return context


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
        return super().form_valid(form)

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


class TaskArchiveView(TaskManagementMixin, LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if self.task.status != Task.Status.ARCHIVED:
            self.task.status = Task.Status.ARCHIVED
            self.task.save(update_fields=["status", "updated_at"])
        return redirect(self.get_success_url())


__all__ = [
    "TaskListView",
    "TaskCreateView",
    "TaskUpdateView",
    "TaskArchiveView",
]
