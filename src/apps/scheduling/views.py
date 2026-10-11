import calendar
from collections import defaultdict
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, TemplateView, View

from apps.tasks.models import Task, TaskAssignment
from apps.workspaces.models import Workspace

from .forms import ScheduleRuleForm
from .models import ScheduleRule, TaskOccurrence
from .services import generate_occurrences


class ScheduleRuleCreateView(LoginRequiredMixin, CreateView):
    model = ScheduleRule
    form_class = ScheduleRuleForm
    template_name = "scheduling/schedule_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.workspace = Workspace.objects.filter(pk=kwargs["workspace_id"]).first()
        self.task = Task.objects.filter(pk=kwargs["task_id"]).first()
        if self.workspace is None or self.task is None:
            raise Http404
        if self.task.workspace_id != self.workspace.pk:
            raise Http404
        if not self.workspace.can_create_tasks(request.user):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workspace"] = self.workspace
        context["task"] = self.task
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["workspace"] = self.workspace
        return kwargs

    def form_valid(self, form):
        rule = form.save(commit=False)
        rule.task = self.task
        rule.created_by = self.request.user
        rule.weekdays = form.cleaned_data["weekdays"]
        rule.save()

        start_date = rule.starts_on
        end_date = rule.ends_on or (start_date + timedelta(days=365))
        generate_occurrences(rule, start_date, end_date)

        assignee = form.cleaned_data.get("assignee")
        if assignee:
            occurrences = self.task.occurrences.filter(
                schedule_rule=rule,
                scheduled_date__gte=start_date,
                scheduled_date__lte=end_date,
            ).prefetch_related("assignments")
            pending = []
            for occurrence in occurrences:
                if occurrence.assignments.filter(user=assignee).exists():
                    continue
                pending.append(TaskAssignment(occurrence=occurrence, user=assignee))
            if pending:
                TaskAssignment.objects.bulk_create(pending)

        messages.success(self.request, "Recorrência criada com sucesso.")
        return redirect(
            reverse("tasks:list", kwargs={"workspace_id": self.workspace.pk})
        )


class TaskOccurrenceDetailView(LoginRequiredMixin, DetailView):
    model = TaskOccurrence
    template_name = "scheduling/occurrence_detail.html"
    context_object_name = "occurrence"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.workspace = Workspace.objects.filter(pk=kwargs["workspace_id"]).first()
        if self.workspace is None or not self.workspace.can_view(request.user):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        occurrence = super().get_object(queryset)
        if occurrence.task.workspace_id != self.workspace.pk:
            raise Http404
        return occurrence

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignable_users = []
        seen = set()

        members = self.workspace.memberships.select_related("user").filter(
            is_active=True,
        )
        for user in [self.workspace.owner] + [item.user for item in members]:
            if user is None or user.pk in seen:
                continue
            seen.add(user.pk)
            assignable_users.append(user)

        context["workspace"] = self.workspace
        context["assignments"] = self.object.assignments.select_related("user").all()
        context["current_user_assignment"] = self.object.assignments.filter(
            user=self.request.user,
        ).first()
        context["assignable_users"] = assignable_users
        context["can_assign_occurrence"] = self.workspace.can_create_tasks(self.request.user)
        return context


class TaskOccurrenceAssignView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.workspace = Workspace.objects.filter(pk=kwargs["workspace_id"]).first()
        if self.workspace is None or not self.workspace.can_view(request.user):
            raise Http404
        if not self.workspace.can_create_tasks(request.user):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        occurrence = TaskOccurrence.objects.filter(
            pk=kwargs["pk"],
            task__workspace=self.workspace,
        ).first()
        if occurrence is None:
            raise Http404

        user_id = request.POST.get("user")
        if not user_id:
            messages.error(request, "Selecione um responsável para a ocorrência.")
            return redirect(
                "scheduling:occurrence-detail",
                workspace_id=self.workspace.pk,
                pk=occurrence.pk,
            )

        user_model = get_user_model()
        try:
            assignee = user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist as exc:
            raise Http404 from exc

        is_valid_member = (
            assignee.pk == self.workspace.owner_id
            or self.workspace.memberships.filter(user=assignee, is_active=True).exists()
        )
        if not is_valid_member:
            raise Http404

        if occurrence.assignments.filter(user=assignee).exists():
            messages.info(request, "Este responsável já está atribuído à ocorrência.")
        else:
            occurrence.assignments.create(user=assignee)
            messages.success(request, "Responsável atribuído com sucesso.")

        return redirect(
            "scheduling:occurrence-detail",
            workspace_id=self.workspace.pk,
            pk=occurrence.pk,
        )


class TaskAssignmentCompleteView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.workspace = Workspace.objects.filter(pk=kwargs["workspace_id"]).first()
        if self.workspace is None or not self.workspace.can_view(request.user):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        assignment = TaskAssignment.objects.select_related("occurrence__task").filter(
            pk=kwargs["assignment_id"],
        ).first()
        if assignment is None:
            raise Http404
        if assignment.occurrence.task.workspace_id != self.workspace.pk:
            raise Http404
        if assignment.user_id != request.user.pk:
            raise Http404

        try:
            assignment.mark_completed(request.user)
            messages.success(request, "Ação concluída com sucesso.")
        except ValueError:
            messages.error(request, "Você só pode concluir sua própria atribuição.")

        return redirect(
            "scheduling:occurrence-detail",
            workspace_id=self.workspace.pk,
            pk=assignment.occurrence_id,
        )


class WorkspaceCalendarView(LoginRequiredMixin, TemplateView):
    template_name = "scheduling/calendar.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        self.workspace = Workspace.objects.filter(pk=kwargs["workspace_id"]).first()
        if self.workspace is None or not self.workspace.can_view(request.user):
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        year = int(self.request.GET.get("year", today.year))
        month = int(self.request.GET.get("month", today.month))

        if not 1 <= month <= 12:
            raise Http404

        month_names = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro",
        }

        month_start = date(year, month, 1)
        month_end = date(year, month, calendar.monthrange(year, month)[1])

        occurrences = (
            TaskOccurrence.objects.filter(
                task__workspace=self.workspace,
                scheduled_date__gte=month_start,
                scheduled_date__lte=month_end,
            )
            .select_related("task")
            .order_by("scheduled_date", "task__title")
        )

        occurrence_map = defaultdict(list)
        for occurrence in occurrences:
            occurrence_map[occurrence.scheduled_date].append(occurrence)

        calendar_rows = []
        for week in calendar.Calendar(firstweekday=0).monthdatescalendar(year, month):
            row = []
            for current_day in week:
                row.append(
                    {
                        "date": current_day,
                        "in_month": current_day.month == month,
                        "is_weekend": current_day.weekday() >= 5,
                        "occurrences": occurrence_map.get(current_day, []),
                    }
                )
            calendar_rows.append(row)

        prev_year, prev_month = self._shift_month(year, month, -1)
        next_year, next_month = self._shift_month(year, month, 1)

        context.update(
            {
                "workspace": self.workspace,
                "calendar_rows": calendar_rows,
                "weekdays": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
                "month_name": month_names[month],
                "month_label": f"{month_names[month]} de {year}",
                "year": year,
                "month": month,
                "previous_month": {"year": prev_year, "month": prev_month},
                "next_month": {"year": next_year, "month": next_month},
                "occurrences_total": occurrences.count(),
            }
        )
        return context

    @staticmethod
    def _shift_month(year, month, delta):
        total_months = (year * 12) + (month - 1) + delta
        target_year, target_month_index = divmod(total_months, 12)
        target_month = target_month_index + 1
        return target_year, target_month


__all__ = [
    "WorkspaceCalendarView",
    "ScheduleRuleCreateView",
    "TaskOccurrenceDetailView",
    "TaskOccurrenceAssignView",
    "TaskAssignmentCompleteView",
]
