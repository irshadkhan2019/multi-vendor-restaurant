from django.urls import path, include
from . import views

app_name = "order"

urlpatterns = [
    path("place_order/", views.place_order, name="place_order"),
    path("payments/", views.payments, name="payments"),
]
