from decimal import Decimal, ROUND_HALF_UP

from flask import Blueprint, abort, current_app, render_template, request, session

from models import catalog
from services.cart_service import cart_summary

shop = Blueprint("shop", __name__)
PRODUCTS_PER_PAGE = 24


def cart_count(cart):
    if not isinstance(cart, dict):
        return 0
    return sum(
        quantity for quantity in cart.values()
        if isinstance(quantity, int) and not isinstance(quantity, bool) and quantity > 0
    )


def parse_optional_id(value, field_name):
    if value is None:
        return None
    try:
        parsed = int(value)
    except ValueError:
        abort(400, description=f"{field_name} debe ser un entero positivo.")
    if parsed < 1:
        abort(400, description=f"{field_name} debe ser un entero positivo.")
    return parsed


@shop.app_template_filter("cop")
def to_cop(value):
    rate = Decimal(str(current_app.config["USD_TO_COP_RATE"]))
    amount = (Decimal(str(value)) * rate).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    formatted = f"{amount:,.0f}".replace(",", ".")
    return f"$ {formatted} COP"


@shop.get("/")
def home():
    categories = catalog.fetch_categories()
    top_products = catalog.fetch_top_products(limit=10)
    return render_template(
        "index.html",
        categories=categories,
        top_products=top_products,
        cart_count=cart_count(session.get("cart", {})),
    )


@shop.get("/tienda")
@shop.get("/catalogo")
def shop_view():
    categories = catalog.fetch_categories()
    category_id = parse_optional_id(request.args.get("category_id"), "category_id")
    subcategory_id = parse_optional_id(
        request.args.get("subcategory_id"), "subcategory_id"
    )
    search = request.args.get("q", "").strip()
    if len(search) > 100:
        abort(400, description="La búsqueda no puede superar 100 caracteres.")
    sort = request.args.get("sort", "featured")
    if sort not in {"featured", "price_asc", "price_desc", "rating_desc"}:
        abort(400, description="El criterio de orden no es válido.")
    all_products = catalog.fetch_products(category_id, subcategory_id, search, sort)
    total_products = len(all_products)
    page = parse_optional_id(request.args.get("page"), "page") or 1
    total_pages = max(1, (total_products + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE)
    if page > total_pages:
        abort(404, description="La página solicitada no existe.")
    start = (page - 1) * PRODUCTS_PER_PAGE
    products = all_products[start:start + PRODUCTS_PER_PAGE]
    return render_template(
        "shop.html",
        categories=categories,
        products=products,
        total_products=total_products,
        category_id=category_id,
        subcategory_id=subcategory_id,
        search=search,
        sort=sort,
        page=page,
        total_pages=total_pages,
        cart_count=cart_count(session.get("cart", {})),
    )


@shop.post("/contacto")
def contact():
    nombre = request.form.get("nombre", "Estimado cliente").strip()
    flash(f"¡Gracias por tu mensaje, {nombre}! Nos pondremos en contacto contigo lo antes posible.", "success")
    return redirect(url_for("shop.home") + "#contacto")


@shop.get("/productos/<string:product_id>")
def product_detail(product_id):
    product = catalog.fetch_product(product_id)
    if product is None:
        abort(404, description="No existe el producto solicitado.")
    return render_template(
        "product_detail.html",
        product=product,
        cart_count=cart_count(session.get("cart", {})),
    )


@shop.get("/carrito")
def cart():
    cart_data = session.get("cart", {})
    if not isinstance(cart_data, dict):
        cart_data = {}
    items, total = cart_summary(cart_data)
    session["cart"] = cart_data
    return render_template(
        "cart.html",
        items=items,
        total=total,
        cart_count=cart_count(cart_data),
    )