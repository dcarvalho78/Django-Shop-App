# cart/urls.py
from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_summary, name="summary"),
    path("add/", views.cart_add, name="add"),
    path("update/", views.cart_update, name="update"),
    path("delete/", views.cart_delete, name="delete"),
]
