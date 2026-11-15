from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check, name="health"),
    path("", include("apps.dashboard.urls")),
    path("admin/", admin.site.urls),
    path("demo/", include("apps.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("workspaces/", include("apps.workspaces.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("scheduling/", include("apps.scheduling.urls")),
]
