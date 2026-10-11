from django.urls import path

from .views import WorkspaceCreateView, WorkspaceDetailView, WorkspaceListView

app_name = "workspaces"

urlpatterns = [
    path("", WorkspaceListView.as_view(), name="list"),
    path("new/", WorkspaceCreateView.as_view(), name="create"),
    path("<uuid:pk>/", WorkspaceDetailView.as_view(), name="detail"),
]
