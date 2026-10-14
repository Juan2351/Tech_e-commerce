from decimal import Decimal

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
