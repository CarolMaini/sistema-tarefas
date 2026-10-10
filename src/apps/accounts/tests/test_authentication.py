import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse


@pytest.mark.django_db
def test_account_pages_are_available(client):
    login = client.get(reverse("account_login"))
    signup = client.get(reverse("account_signup"))
    reset = client.get(reverse("account_reset_password"))

    assert login.status_code == 200
    assert b"Entre na sua conta" in login.content
    assert b"auth.css" in login.content
    assert signup.status_code == 200
    assert b"Crie sua conta" in signup.content
    assert b"auth.css" in signup.content
    assert reset.status_code == 200


@pytest.mark.django_db
def test_user_can_log_in_with_verified_email(client):
    user = get_user_model().objects.create_user(
        username="alice",
        email="alice@example.com",
        password="Strong-password-123!",
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        primary=True,
        verified=True,
    )

    response = client.post(
        reverse("account_login"),
        {"login": user.email, "password": "Strong-password-123!"},
    )

    assert response.status_code == 302
    assert str(user.pk) == client.session["_auth_user_id"]


@pytest.mark.django_db
def test_signup_requires_email_verification(client):
    response = client.post(
        reverse("account_signup"),
        {
            "username": "new-alice",
            "email": "new-alice@example.com",
            "password1": "Strong-password-123!",
            "password2": "Strong-password-123!",
        },
    )

    assert response.status_code == 302
    user = get_user_model().objects.get(email="new-alice@example.com")
    assert EmailAddress.objects.get(user=user).verified is False
    assert len(mail.outbox) == 1


def test_google_login_route_is_registered():
    assert reverse("google_login") == "/accounts/google/login/"