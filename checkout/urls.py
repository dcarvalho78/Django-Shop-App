from django.urls import path
from . import views

urlpatterns = [
    
    path('checkout_success', views.checkout_success, name='checkout_success'),
    path('checkout_failed', views.checkout_failed, name='checkout_failed'),
    path('checkout', views.checkout, name='checkout'),
    path('billing_info', views.billing_info, name="billing_info"),
    path('process_order', views.process_order, name="process_order"),
    path('shipped_dash', views.shipped_dash, name="shipped_dash"),
    path('not_shipped_dash', views.not_shipped_dash, name="not_shipped_dash"),
    path('orders/<int:pk>', views.orders, name='orders'),
]
