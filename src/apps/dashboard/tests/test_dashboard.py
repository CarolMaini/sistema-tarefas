import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.workspaces.models import Workspace


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    response = client.get(reverse("dashboard:home"))

    assert response.status_code == 302
    assert "/accounts/login" in response.url


@pytest.mark.django_db
def test_dashboard_logged_user_sees_workspace_summary(client):
    user = get_user_model().objects.create_user(
        username="dashboard-user",
        email="dashboard@example.com",
        password="Strong-password-123!",
    )
    Workspace.objects.create(name="Workspace Alpha", owner=user)

    client.force_login(user)
    response = client.get(reverse("dashboard:home"))

    assert response.status_code == 200
    assert "Dashboard" in response.content.decode()
    assert "Workspace Alpha" in response.content.decode()
