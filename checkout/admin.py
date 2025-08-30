# checkout/admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Order, OrderItem, ShippingAddress

# -------------------------
# Orders
# -------------------------

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'full_name', 'email', 'amount_paid',
        'status', 'shipped', 'date_ordered', 'date_shipped'
    )
    list_filter = ('status', 'shipped', 'date_ordered')
    list_editable = ('status', 'shipped')
    search_fields = ('full_name', 'email', 'id')


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'shipping_first_name', 'shipping_last_name',
        'shipping_email', 'shipping_country'
    )

admin.site.register(Order, OrderAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)

# -------------------------
# Accounts (als Proxy von auth.User, OHNE neues app_label)
# -------------------------

# Standard-User aus dem Admin abmelden, damit es nicht doppelt auftaucht
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Proxy-Modell: gleicher DB-Table, anderer Anzeigename
class Account(User):
    class Meta:
        proxy = True
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

@admin.register(Account)
class AccountAdmin(DjangoUserAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'is_active', 'date_joined')
    search_fields = ('first_name', 'last_name', 'email', 'username')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
