# checkout/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import login, get_user_model
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Max

from cart.cart import Cart
from checkout.forms import ShippingForm, PaymentForm
from checkout.models import ShippingAddress, Order, OrderItem


def orders(request, pk):
    order = get_object_or_404(Order, id=pk)
    items = OrderItem.objects.filter(order=order)

    if request.method == "POST":
        status = (request.POST.get('shipping_status') or '').lower()
        if status == "true":
            order.shipped = True
            order.date_shipped = timezone.now()
        else:
            order.shipped = False
            order.date_shipped = None
        order.save(update_fields=["shipped", "date_shipped"])
        messages.success(request, "Shipping status updated")
        return redirect('home')

    return render(request, 'checkout/orders.html', {"order": order, "items": items})


def not_shipped_dash(request):
    orders_qs = Order.objects.filter(shipped=False)
    if request.method == "POST":
        num = request.POST.get('num')
        Order.objects.filter(id=num).update(shipped=True, date_shipped=timezone.now())
        messages.success(request, "Shipping status updated")
        return redirect('home')
    return render(request, "checkout/not_shipped_dash.html", {"orders": orders_qs})


def shipped_dash(request):
    orders_qs = Order.objects.filter(shipped=True)
    if request.method == "POST":
        num = request.POST.get('num')
        Order.objects.filter(id=num).update(shipped=False, date_shipped=None)
        messages.success(request, "Shipping status updated")
        return redirect('home')
    return render(request, "checkout/shipped_dash.html", {"orders": orders_qs})


@require_POST
def billing_info(request):
    cart = Cart(request)
    form = ShippingForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please correct the errors below.")
        return render(request, "checkout.html", {
            "cart_products": cart.get_prods,
            "quantities": cart.get_quants,
            "totals": cart.cart_total(),
            "shipping_form": form,
        })

    request.session['my_shipping'] = form.cleaned_data.copy()

    return render(request, "checkout/billing_info.html", {
        "cart_products": cart.get_prods,
        "quantities": cart.get_quants,
        "totals": cart.cart_total(),
        "shipping_form": form,
        "payment_form": PaymentForm(),
    })


def _unique_username_from_email(email: str) -> str:
    base = (email.split("@", 1)[0] or "user")
    base = "".join(ch for ch in base if ch.isalnum()) or "user"
    User = get_user_model()
    username = base
    i = 1
    while User.objects.filter(username__iexact=username).exists():
        i += 1
        username = f"{base}{i}"
    return username


@require_POST
@transaction.atomic
def process_order(request):
    cart = Cart(request)
    totals = cart.cart_total()

    form = ShippingForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please fix the highlighted fields.")
        return render(request, "checkout.html", {
            "cart_products": cart.get_prods,
            "quantities": cart.get_quants,
            "totals": totals,
            "shipping_form": form,
        })

    cd = form.cleaned_data

    User = get_user_model()
    user_to_attach = request.user if request.user.is_authenticated else None

    if not user_to_attach and (cd.get('account_password1') or cd.get('account_password2')):
        email = cd['shipping_email']
        existing = User.objects.filter(email__iexact=email).order_by('id').first()
        if existing:
            user_to_attach = existing
            messages.info(
                request,
                "An account with this email already exists. "
                "The order will be linked to your account. "
                "You can set a password later via 'Forgot Password'."
            )
        else:
            username = _unique_username_from_email(email)
            user_to_attach = User.objects.create_user(
                username=username,
                email=email,
                first_name=cd['shipping_first_name'],
                last_name=cd['shipping_last_name'],
                password=cd['account_password1'],
            )
            login(request, user_to_attach, backend='accounts.backends.EmailOrUsernameBackend')
            messages.success(request, "Account created and logged in 🎉")

    shipping_address = ShippingAddress.objects.create(
        shipping_first_name=cd['shipping_first_name'],
        shipping_last_name=cd['shipping_last_name'],
        shipping_email=cd['shipping_email'],
        shipping_address1=cd['shipping_address1'],
        shipping_address2=cd.get('shipping_address2') or None,
        shipping_city=cd['shipping_city'],
        shipping_state=cd.get('shipping_state') or None,
        shipping_zipcode=cd.get('shipping_zipcode') or None,
        shipping_country=cd['shipping_country'],
    )

    first_name = cd['shipping_first_name']
    last_name = cd['shipping_last_name']
    full_name = f"{first_name} {last_name}"
    email = cd['shipping_email']

    order = Order.objects.create(
        user=user_to_attach if user_to_attach else (request.user if request.user.is_authenticated else None),
        full_name=full_name,
        email=email,
        shipping_address=shipping_address,
        amount_paid=totals,
    )

    for product in cart.get_prods():
        price = product.sale_price if getattr(product, "is_sale", False) else product.price
        qty = int(cart.get_quants().get(str(product.id)) or 1)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            price=price,
        )

    try:
        cart.clear()
    except AttributeError:
        request.session.pop("session_key", None)

    messages.success(request, "Order successfully completed.")
    return redirect('checkout:checkout_success')


def checkout(request):
    cart = Cart(request)
    shipping_form = ShippingForm()
    return render(request, "checkout.html", {
        "cart_products": cart.get_prods,
        "quantities": cart.get_quants,
        "totals": cart.cart_total(),
        "shipping_form": shipping_form,
    })


def checkout_success(request):
    return render(request, "checkout/checkout_success.html")


def checkout_failed(request):
    return render(request, "checkout/checkout_failed.html")


@login_required
def orders_list(request):
    qs = Order.objects.all() if request.user.is_superuser else Order.objects.filter(user=request.user)
    orders = qs.select_related("shipping_address").order_by('-date_ordered', '-id')
    return render(request, "checkout/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, pk: int):
    # Superusers can see any order; regular users only their own.
    base_qs = Order.objects.select_related("shipping_address")
    order = (
        get_object_or_404(base_qs, pk=pk)
        if request.user.is_superuser
        else get_object_or_404(base_qs, pk=pk, user=request.user)
    )

    # Don't rely on order.orderitem_set; query via the FK explicitly.
    items = (
        OrderItem.objects
        .filter(order=order)
        .select_related("product")
        .all()
    )

    return render(request, "checkout/my_order_detail.html", {
        "order": order,
        "items": items,
    })



@login_required
def dashboard(request):
    qs = Order.objects.all() if request.user.is_superuser else Order.objects.filter(user=request.user)
    orders = qs.select_related("shipping_address").order_by('-date_ordered', '-id')
    kpis = {
        "total_count": qs.count(),
        "shipped_count": qs.filter(shipped=True).count(),
        "unshipped_count": qs.filter(shipped=False).count(),
        "last_order": qs.aggregate(Max("date_ordered"))["date_ordered__max"],
        "total_amount": qs.aggregate(Sum("amount_paid"))["amount_paid__sum"] or 0,
    }
    return render(request, "checkout/dashboard.html", {"orders": orders, "kpis": kpis})


my_orders = orders_list
my_order_detail = order_detail
