from django.urls import path, include
from . import views

app_name = "accounts"

urlpatterns = [
    path("registerUser/", views.registerUser, name="registerUser"),
]
