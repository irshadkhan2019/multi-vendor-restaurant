from django.urls import path
from accounts.views import custDashboard
from . import views

app_name = "customer"

urlpatterns = [
    # path("", views.custDashboard, name="custDashboard"),
    path("profile/", views.cprofile, name="cprofile"),
]
