from django.urls import path

from .demo import demo_login, demo_logout

app_name = "accounts"

urlpatterns = [
    path("entrar/", demo_login, name="demo_login"),
    path("sair/", demo_logout, name="demo_logout"),
]
