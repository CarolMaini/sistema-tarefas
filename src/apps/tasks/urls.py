from django.urls import path

from .views import TaskCreateView, TaskListView

app_name = "tasks"

urlpatterns = [
    path("workspaces/<uuid:workspace_id>/tasks/", TaskListView.as_view(), name="list"),
    path("workspaces/<uuid:workspace_id>/tasks/new/", TaskCreateView.as_view(), name="create"),
]
