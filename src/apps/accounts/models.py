from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    timezone = models.CharField(max_length=64, default="America/Sao_Paulo")

    class Meta:
        db_table = "accounts_user"

    def __str__(self):
        return self.display_name or self.username
