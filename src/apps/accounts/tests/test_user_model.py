import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_custom_user_model_exists():
    User = get_user_model()

    assert User._meta.app_label == "accounts"
    assert User._meta.get_field("email").unique is True
    assert User._meta.get_field("timezone").default == "America/Sao_Paulo"

    user = User.objects.create_user(
        username="alice",
        email="alice@example.com",
        password="secret123",
        display_name="Alice",
    )

    assert user.email == "alice@example.com"
    assert user.display_name == "Alice"
    assert user.check_password("secret123") is True
