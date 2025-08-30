from django.urls import path
from . import views

app_name = "checkout"

urlpatterns = [
 path("checkout/", views.checkout, name="checkout"),
    path("process/", views.process_order, name="process_order"),  # <- für das form action
    path("success/", views.checkout_success, name="checkout_success"),
    path("failed/", views.checkout_failed, name="checkout_failed"),

    # Kunde: eigene Bestellungen
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/<int:pk>/", views.my_order_detail, name="my_order_detail"),

    # Vorhandene Admin-/Dash-Routen (lass sie, falls du sie brauchst)
    path("orders/<int:pk>/", views.orders, name="orders"),
    path("dash/not-shipped/", views.not_shipped_dash, name="not_shipped_dash"),
    path("dash/shipped/", views.shipped_dash, name="shipped_dash"),
     path("dashboard/", views.dashboard, name="dashboard"),
]
   