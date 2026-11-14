from decimal import Decimal, ROUND_HALF_UP

from models.auth_model import get_vip_discount_rate
from models.catalog import fetch_product, fetch_products_by_ids


class CartError(ValueError):
    pass


class CartProductNotFound(CartError):
    pass


class CartItemNotFound(CartError):
    pass


class CartStockError(CartError):
    pass


def add_product(cart, product_id, quantity):
    if not isinstance(product_id, str) or not product_id.strip():
        raise CartError("product_id debe ser un texto no vacío.")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        raise CartError("quantity debe ser un entero mayor que cero.")

    product = fetch_product(product_id.strip())
    if product is None:
        raise CartProductNotFound("El producto solicitado no existe.")
    new_quantity = cart.get(product.id_producto, 0) + quantity
    if new_quantity > product.stock:
        raise CartStockError("La cantidad solicitada supera el stock disponible.")
    cart[product.id_producto] = new_quantity
    return product, new_quantity


def update_quantity(cart, product_id, quantity):
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        raise CartError("quantity debe ser un entero mayor que cero.")
    if product_id not in cart:
        raise CartItemNotFound("El producto no está en el carrito.")
    product = fetch_product(product_id)
    if product is None:
        raise CartProductNotFound("El producto solicitado no existe.")
    if quantity > product.stock:
        raise CartStockError("La cantidad solicitada supera el stock disponible.")
    cart[product_id] = quantity
    return product


def cart_summary(cart):
    products = fetch_products_by_ids(list(cart))
    available_ids = {product.id_producto for product in products}
    for product_id in list(cart):
        if product_id not in available_ids:
            del cart[product_id]

    items = []
    total = Decimal("0.00")
    for product in products:
        quantity = cart[product.id_producto]
        subtotal = product.precio * quantity
        total += subtotal
        items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })
    return items, total


def calculate_cart_totals(subtotal: Decimal, user=None, items=None, coupon=None):
    subtotal_dec = Decimal(str(subtotal))
    discount_rate = get_vip_discount_rate(user)
    vip_discount_amount = subtotal_dec * discount_rate

    coupon_discount_amount = Decimal("0.00")
    coupon_percent = 0
    coupon_code = ""
    coupon_category_name = None

    if isinstance(coupon, dict) and coupon.get("activo", 1):
        try:
            pct = Decimal(str(coupon.get("porcentaje_descuento", 0)))
        except Exception:
            pct = Decimal("0")
        if pct > Decimal("0"):
            target_cat = coupon.get("id_main_cat")
            if target_cat not in (None, "", 0, "0") and items is not None:
                eligible_subtotal = sum(
                    (
                        Decimal(str(item["subtotal"]))
                        for item in items
                        if str(getattr(item.get("product"), "id_main_cat", "")) == str(target_cat)
                    ),
                    Decimal("0.00"),
                )
            else:
                eligible_subtotal = subtotal_dec

            if eligible_subtotal > Decimal("0.00"):
                coupon_discount_amount = eligible_subtotal * (pct / Decimal("100"))
                coupon_percent = int(pct)
                coupon_code = str(coupon.get("codigo", "")).upper()
                coupon_category_name = coupon.get("categoria_nombre")

    total_discount = min(subtotal_dec, vip_discount_amount + coupon_discount_amount)
    final_total = max(Decimal("0.00"), subtotal_dec - total_discount)
    return {
        "subtotal": subtotal_dec,
        "discount_rate": discount_rate,
        "discount_percent": int(discount_rate * 100),
        "vip_discount_amount": vip_discount_amount,
        "coupon_code": coupon_code,
        "coupon_percent": coupon_percent,
        "coupon_discount_amount": coupon_discount_amount,
        "coupon_category_name": coupon_category_name,
        "discount_amount": total_discount,
        "total": final_total,
        "is_vip": discount_rate > Decimal("0.00"),
    }


def _owner_key(user) -> str:
    if isinstance(user, dict) and user.get("id") is not None:
        return f"user:{user['id']}"
    return "__guest__"


def get_session_cart(session_obj) -> dict:
    """Obtiene el carrito aislado correspondiente al usuario actual en sesión."""
    current_owner = _owner_key(session_obj.get("user"))
    recorded_owner = session_obj.get("_cart_owner")
    user_carts = session_obj.get("user_carts")
    if not isinstance(user_carts, dict):
        user_carts = {}

    raw_cart = session_obj.get("cart")
    if not isinstance(raw_cart, dict):
        raw_cart = {}

    if recorded_owner is None:
        # Primera vez o test que inyectó session["cart"] directamente
        session_obj["_cart_owner"] = current_owner
        user_carts[current_owner] = dict(raw_cart)
        session_obj["user_carts"] = user_carts
        return raw_cart

    if recorded_owner != current_owner:
        # Cambió el usuario sin pasar por switch_cart_owner: guardar el anterior y cargar el nuevo
        user_carts[recorded_owner] = dict(raw_cart)
        new_cart = dict(user_carts.get(current_owner, {}))
        session_obj["cart"] = new_cart
        session_obj["_cart_owner"] = current_owner
        session_obj["user_carts"] = user_carts
        return new_cart

    user_carts[current_owner] = dict(raw_cart)
    session_obj["user_carts"] = user_carts
    return raw_cart


def save_session_cart(session_obj, cart: dict) -> None:
    """Guarda el carrito activo sincronizándolo con el espacio aislado del usuario actual."""
    clean_cart = dict(cart) if isinstance(cart, dict) else {}
    current_owner = _owner_key(session_obj.get("user"))
    user_carts = session_obj.get("user_carts")
    if not isinstance(user_carts, dict):
        user_carts = {}
    user_carts[current_owner] = dict(clean_cart)
    session_obj["user_carts"] = user_carts
    session_obj["_cart_owner"] = current_owner
    session_obj["cart"] = clean_cart


def switch_cart_owner(session_obj, new_user=None) -> None:
    """Guarda el carrito del usuario saliente y activa el carrito aislado del usuario entrante."""
    previous_owner = session_obj.get("_cart_owner") or _owner_key(session_obj.get("user"))
    user_carts = session_obj.get("user_carts")
    if not isinstance(user_carts, dict):
        user_carts = {}

    current_cart = session_obj.get("cart")
    if isinstance(current_cart, dict):
        user_carts[previous_owner] = dict(current_cart)

    new_owner = _owner_key(new_user)
    if new_owner == "__guest__":
        # Al cerrar sesión, el carrito de invitado arranca vacío para no exponer productos previos
        user_carts["__guest__"] = {}
        next_cart = {}
    else:
        next_cart = dict(user_carts.get(new_owner, {}))

    session_obj["user_carts"] = user_carts
    session_obj["_cart_owner"] = new_owner
    session_obj["cart"] = next_cart
    session_obj.pop("checkout_token", None)
