from django.db import models
from shop import settings
from store.models import Product
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver 
import datetime

class ShippingAddress(models.Model):
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.EmailField(max_length=255)  # Changed to EmailField
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Shipping Addresses"  # Corrected pluralization

    def __str__(self):
        return f'Shipping Address - {self.id}'

class Order(models.Model):
    # Link to the user placing the order
    user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    null=True,
    blank=True
)

    # Basic order information
    full_name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(max_length=15000)
    amount_paid = models.DecimalField(max_digits=9, decimal_places=2)  # Increased max_digits
    date_ordered = models.DateTimeField(auto_now_add=True)
    
    # Shipping information
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    
    # Order status
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('R', 'Processing'),  # changed key from 'P' to 'R' to avoid duplicates
        ('S', 'Shipped'),
        ('D', 'Delivered'),
        ('C', 'Cancelled'),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    class Meta:
        ordering = ['-date_ordered']  # Newest orders first

    def __str__(self):
        return f'Order #{self.id} - {self.full_name}'


@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.pk:
        original = Order.objects.get(pk=instance.pk)
        if instance.shipped and not original.shipped:
            instance.date_shipped = datetime.datetime.now()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)  # Changed to PROTECT
    quantity = models.PositiveIntegerField(default=1)  # Changed from PositiveBigInteger
    price = models.DecimalField(max_digits=7, decimal_places=2)
    
    class Meta:
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f'{self.quantity} x {self.product.name} (Order #{self.order.id})'

    @property
    def total_price(self):
        return self.quantity * self.price