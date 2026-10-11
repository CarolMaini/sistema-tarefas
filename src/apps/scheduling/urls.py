from django.urls import path

from .views import (
    ScheduleRuleCreateView,
    TaskAssignmentCompleteView,
    TaskOccurrenceAssignView,
    TaskOccurrenceDetailView,
    WorkspaceCalendarView,
)

app_name = "scheduling"

urlpatterns = [
    path(
        "workspaces/<uuid:workspace_id>/tasks/<uuid:task_id>/rules/new/",
        ScheduleRuleCreateView.as_view(),
        name="create",
    ),
    path(
        "workspaces/<uuid:workspace_id>/occurrences/<uuid:pk>/",
        TaskOccurrenceDetailView.as_view(),
        name="occurrence-detail",
    ),
    path(
        "workspaces/<uuid:workspace_id>/occurrences/<uuid:pk>/assign/",
        TaskOccurrenceAssignView.as_view(),
        name="occurrence-assign",
    ),
    path(
        "workspaces/<uuid:workspace_id>/occurrences/<uuid:pk>/complete/<int:assignment_id>/",
        TaskAssignmentCompleteView.as_view(),
        name="complete-assignment",
    ),
    path(
        "workspaces/<uuid:workspace_id>/calendar/",
        WorkspaceCalendarView.as_view(),
        name="calendar",
    ),
]
