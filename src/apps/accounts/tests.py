from django.test import TestCase, override_settings
from django.urls import reverse

from apps.workspaces.models import Workspace


@override_settings(DEMO_ACCESS_ENABLED=True)
class DemoAccessTests(TestCase):
    def enter_demo(self):
        self.client.post(reverse("accounts:demo_login"))
        return self.client.get(reverse("dashboard:home"))

    def test_demo_login_creates_session_and_sample_workspace(self):
        response = self.enter_demo()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertTrue(self.client.session.get("demo_access"))
        self.assertTrue(
            Workspace.objects.filter(
                owner__email="visitante@organizador.demo",
                name="Espaço de demonstração",
            ).exists()
        )

    def test_demo_user_can_open_protected_workspace_and_task_routes(self):
        self.enter_demo()
        workspace = Workspace.objects.get(name="Espaço de demonstração")

        workspace_response = self.client.get(
            reverse("workspaces:detail", kwargs={"pk": workspace.pk})
        )
        tasks_response = self.client.get(
            reverse("tasks:list", kwargs={"workspace_id": workspace.pk})
        )
        calendar_response = self.client.get(
            reverse("scheduling:calendar", kwargs={"workspace_id": workspace.pk})
        )

        self.assertEqual(workspace_response.status_code, 200)
        self.assertEqual(tasks_response.status_code, 200)
        self.assertEqual(calendar_response.status_code, 200)

    def test_demo_session_cannot_change_shared_data(self):
        self.enter_demo()
        workspace = Workspace.objects.get(name="Espaço de demonstração")

        response = self.client.post(
            reverse("tasks:create", kwargs={"workspace_id": workspace.pk}),
            {"title": "Não deve ser criado", "description": ""},
        )

        self.assertEqual(response.status_code, 403)
