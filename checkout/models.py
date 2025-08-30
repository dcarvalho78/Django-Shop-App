from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from store.models import Product

from django.conf import settings

class ShippingAddress(models.Model):
    shipping_first_name = models.CharField(max_length=255)
    shipping_last_name = models.CharField(max_length=255)
    shipping_email = models.EmailField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Shipping Addresses"

    def __str__(self):
        return f'Shipping Address - {self.id}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    amount_paid = models.DecimalField(max_digits=9, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('R', 'Processing'),
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('C', 'Cancelled'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')


@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    # If shipped is False, clear the date
    if not instance.shipped:
        instance.date_shipped = None
    else:
        # Prevent empty string or None: set current time if date_shipped is invalid
        if not instance.date_shipped or instance.date_shipped == "":
            instance.date_shipped = timezone.now()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f'{self.quantity} x {self.product.name} (Order #{self.order.id})'

    @property
    def total_price(self):
        return self.quantity * self.price
