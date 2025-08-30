# cart/cart.py
from decimal import Decimal
from store.models import Product


class Cart:
    """
    Warenkorb auf Basis der Session.
    - Primärer Session-Key bleibt 'session_key' (kompatibel zu deinem Code).
    - Fallback liest ggf. alten Key 'cart', falls er irgendwo gesetzt wurde.
    """

    SESSION_KEY = 'session_key'
    FALLBACK_KEYS = ('cart',)  # optionaler Fallback

    def __init__(self, request):
        self.session = request.session
        self.request = request

        cart = self.session.get(self.SESSION_KEY)

        # Fallback: Falls an anderer Stelle 'cart' genutzt wurde
        if cart is None:
            for k in self.FALLBACK_KEYS:
                cart = self.session.get(k)
                if cart is not None:
                    # migriere freundlich auf den primären Key
                    self.session[self.SESSION_KEY] = cart
                    # optional: alten Key aufräumen
                    try:
                        del self.session[k]
                    except KeyError:
                        pass
                    break

        # Wenn immer noch nichts da ist: initialisieren
        if cart is None:
            cart = {}
            self.session[self.SESSION_KEY] = cart

        # interne Referenz
        self.cart = cart

    # --------------------------------------------------------------------- #
    # Mutationen
    # --------------------------------------------------------------------- #
    def add(self, product, quantity=1, override_quantity=False):
        """
        Produkt zum Warenkorb hinzufügen.
        - quantity <= 0 -> keine Aktion (oder löschen, je nach Wunsch)
        - override_quantity=True: setzt die Menge exakt auf 'quantity'
        - override_quantity=False: addiert zur bestehenden Menge
        """
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if quantity <= 0:
            # keine negative/Null-Mengen addieren
            return

        product_id = str(product.id)

        if override_quantity:
            self.cart[product_id] = quantity
        else:
            self.cart[product_id] = self.cart.get(product_id, 0) + quantity

        self.session.modified = True

    def update(self, product, quantity):
        """
        Setzt die Menge eines Produkts direkt.
        - quantity <= 0 -> Produkt aus dem Warenkorb entfernen.
        """
        product_id = str(product)
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if quantity <= 0:
            if product_id in self.cart:
                del self.cart[product_id]
        else:
            self.cart[product_id] = quantity

        self.session.modified = True
        return self.cart

    def delete(self, product):
        """
        Entfernt ein Produkt vollständig aus dem Warenkorb.
        """
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True

    # --------------------------------------------------------------------- #
    # Lese-APIs (werden in Templates/Views verwendet)
    # --------------------------------------------------------------------- #
    def __len__(self):
        """
        Summe aller Stückzahlen über alle Positionen.
        """
        return sum(int(qty) for qty in self.cart.values())

    def get_quants(self):
        """
        Gibt das Mengen-Dict zurück: { 'product_id': qty, ... }
        """
        return self.cart

    def get_prods(self):
        """
        Gibt die Produkt-Query (als Liste) in der Reihenfolge der Cart-Keys zurück.
        """
        ids_in_order = list(self.cart.keys())
        qs = Product.objects.filter(id__in=ids_in_order)

        # Mapping für schnelle Zuordnung
        prod_by_id = {str(p.id): p for p in qs}
        # Reihenfolge wie im Warenkorb
        return [prod_by_id[pid] for pid in ids_in_order if pid in prod_by_id]

    def cart_total(self):
        """
        Gesamtbetrag über alle Positionen (Decimal).
        Nutzt sale_price falls is_sale=True, sonst price.
        """
        total = Decimal('0.00')

        # Einmalig alle Produkte holen
        ids_in_cart = list(self.cart.keys())
        products = Product.objects.filter(id__in=ids_in_cart)
        price_map = {}
        for p in products:
            price_map[str(p.id)] = (p.sale_price if getattr(p, 'is_sale', False) else p.price)

        # Summieren
        for pid, qty in self.cart.items():
            try:
                qty_int = int(qty)
            except (TypeError, ValueError):
                qty_int = 1
            price = price_map.get(pid, Decimal('0.00'))
            if price is None:
                price = Decimal('0.00')
            total += (price * qty_int)

        return total
