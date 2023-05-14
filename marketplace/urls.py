from django.urls import path
from . import views

app_name = "market"

urlpatterns = [
    path("", views.marketplace, name="marketplace"),
    path("<slug:vendor_slug>/", views.vendor_detail, name="vendor_detail"),
    # Add to Cart
    path("add_to_cart/<int:food_id>/", views.add_to_cart, name="add_to_cart"),
    path("decrease_cart/<int:food_id>/", views.decrease_cart, name="decrease_cart"),
    # show cart Items
    path("show/cart", views.cart, name="cart"),
    # DELETE CART ITEM
    path("delete_cart/<int:cart_id>/", views.delete_cart, name="delete_cart"),
]
