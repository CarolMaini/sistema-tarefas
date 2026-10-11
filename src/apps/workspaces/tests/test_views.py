import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.workspaces.models import Workspace


@pytest.mark.django_db
def test_workspace_list_requires_login(client):
    response = client.get(reverse("workspaces:list"))

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


@pytest.mark.django_db
def test_manager_can_create_workspace(client):
    user = get_user_model().objects.create_user(
        username="manager",
        email="manager@example.com",
        password="Strong-password-123!",
    )
    client.force_login(user)

    response = client.post(
        reverse("workspaces:create"),
        {
            "name": "Equipe Financeira",
            "description": "Planejamento do mês.",
        },
    )

    assert response.status_code == 302
    assert Workspace.objects.filter(name="Equipe Financeira", owner=user).exists()
