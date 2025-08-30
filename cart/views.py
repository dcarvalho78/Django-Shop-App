# cart/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.template.loader import render_to_string

from .cart import Cart
from store.models import Product


def cart_summary(request):
    cart = Cart(request)
    context = {
        "cart": cart,
        "cart_products": cart.get_prods(),   # optional nutzbar im Template
        "quantities": cart.get_quants(),
        "totals": cart.cart_total(),
    }
    return render(request, "cart_summary.html", context)


# ---- interne Helper zum Rendern der Offcanvas-Fragmente ----
def _mini_fragments(request, cart: Cart):
    ctx = {
        "cart": cart,
        "quants": cart.get_quants(),
        "totals": cart.cart_total(),
    }
    body_html = render_to_string("cart/_mini_cart_items.html", ctx, request=request)
    footer_html = render_to_string("cart/_mini_cart_footer.html", ctx, request=request)
    return {"body": body_html, "footer": footer_html, "qty": len(cart)}


@require_POST
def cart_add(request):
    # erwartet: product_id, product_qty, action='post'
    if request.POST.get('action') != 'post':
        return JsonResponse({"error": "bad action"}, status=400)

    try:
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty', 1))
    except (TypeError, ValueError):
        return JsonResponse({"error": "bad params"}, status=400)

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, quantity=product_qty)

    return JsonResponse(_mini_fragments(request, cart))


@require_http_methods(["POST", "GET"])
def cart_delete(request):
    # AJAX (POST) oder Fallback-Link (GET ?product_id=..)
    pid = request.POST.get('product_id') if request.method == "POST" else request.GET.get('product_id')
    try:
        product_id = int(pid)
    except (TypeError, ValueError):
        if request.method == "POST":
            return JsonResponse({"error": "bad product_id"}, status=400)
        return redirect("cart_summary")

    cart = Cart(request)
    cart.delete(product=product_id)

    if request.method == "POST":
        return JsonResponse(_mini_fragments(request, cart))
    return redirect("cart_summary")


@require_POST
def cart_update(request):
    # erwartet: product_id, product_qty, action='post'
    if request.POST.get('action') != 'post':
        return JsonResponse({"error": "bad action"}, status=400)

    try:
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
    except (TypeError, ValueError):
        return JsonResponse({"error": "bad params"}, status=400)

    cart = Cart(request)
    cart.update(product=product_id, quantity=product_qty)

    return JsonResponse(_mini_fragments(request, cart))
