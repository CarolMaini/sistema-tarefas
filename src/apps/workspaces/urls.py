from django.urls import path

from .views import (
    WorkspaceCreateView,
    WorkspaceDetailView,
    WorkspaceListView,
    WorkspaceMemberAddView,
    WorkspaceMemberRemoveView,
)

app_name = "workspaces"

urlpatterns = [
    path("", WorkspaceListView.as_view(), name="list"),
    path("new/", WorkspaceCreateView.as_view(), name="create"),
    path("<uuid:pk>/members/add/", WorkspaceMemberAddView.as_view(), name="member-add"),
    path(
        "<uuid:pk>/members/<int:membership_id>/remove/",
        WorkspaceMemberRemoveView.as_view(),
        name="member-remove",
    ),
    path("<uuid:pk>/", WorkspaceDetailView.as_view(), name="detail"),
]
