from django.urls import path, include
from . import views

app_name = "vendor"

urlpatterns = [
    path("profile/", views.vprofile, name="vprofile"),
    path("menu-builder/", views.menu_builder, name="menu_builder"),
    path(
        "menu-builder/category/<int:pk>/",
        views.fooditems_by_category,
        name="fooditems_by_category",
    ),
]
