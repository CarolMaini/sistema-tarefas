from django.urls import path

from .views import (
    TaskArchiveView,
    TaskAuditHistoryView,
    TaskCreateView,
    TaskListView,
    TaskUpdateView,
)

app_name = "tasks"

urlpatterns = [
    path("workspaces/<uuid:workspace_id>/tasks/", TaskListView.as_view(), name="list"),
    path(
        "workspaces/<uuid:workspace_id>/tasks/<uuid:task_id>/history/",
        TaskAuditHistoryView.as_view(),
        name="history",
    ),
    path("workspaces/<uuid:workspace_id>/tasks/new/", TaskCreateView.as_view(), name="create"),
    path(
        "workspaces/<uuid:workspace_id>/tasks/<uuid:task_id>/edit/",
        TaskUpdateView.as_view(),
        name="update",
    ),
    path(
        "workspaces/<uuid:workspace_id>/tasks/<uuid:task_id>/archive/",
        TaskArchiveView.as_view(),
        name="archive",
    ),
]
