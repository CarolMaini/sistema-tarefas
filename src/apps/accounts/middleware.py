from django.conf import settings
from django.http import HttpResponseForbidden


class DemoReadOnlyMiddleware:
    """Expose demo availability and prevent visitors from changing shared data."""

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.demo_access_enabled = settings.DEMO_ACCESS_ENABLED
        if (
            request.session.get("demo_access")
            and request.method not in self.SAFE_METHODS
        ):
            return HttpResponseForbidden(
                "O ambiente público está em modo de demonstração e não permite alterações."
            )
        return self.get_response(request)
