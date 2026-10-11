from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("workspaces/", include("apps.workspaces.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("scheduling/", include("apps.scheduling.urls")),
]
