from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path(
        "orders/<int:order_id>/confirmation/", views.order_confirmation, name="order_confirmation"
    ),
]
