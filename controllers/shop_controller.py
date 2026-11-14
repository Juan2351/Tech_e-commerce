from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import re
import secrets
import sqlite3
from urllib.parse import quote

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from controllers.auth_controller import login_required
from models import catalog
from models.auth_model import get_user_by_id, get_vip_discount_rate
from models.database import get_db
from services.cart_service import (
    calculate_cart_totals,
    cart_summary,
    get_session_cart,
    save_session_cart,
)

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
    return format_cop_amount(amount)


@shop.app_template_filter("cop_amount")
def format_cop_amount(value):
    amount = Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
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
        cart_count=cart_count(get_session_cart(session)),
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
        cart_count=cart_count(get_session_cart(session)),
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
        cart_count=cart_count(get_session_cart(session)),
    )


@shop.get("/carrito")
def cart():
    cart_data = get_session_cart(session)
    user_session = session.get("user")
    items, subtotal = cart_summary(cart_data)
    applied_code = session.get("applied_coupon", "")
    active_coupon = catalog.get_coupon_by_code(applied_code) if applied_code else None
    if applied_code and not active_coupon:
        session.pop("applied_coupon", None)
    pricing = calculate_cart_totals(
        subtotal, user_session, items=items, coupon=active_coupon
    )
    save_session_cart(session, cart_data)
    if items and not session.get("checkout_token"):
        session["checkout_token"] = secrets.token_urlsafe(32)

    checkout_defaults = {
        "nombre": "",
        "telefono": "",
        "correo": "",
        "direccion": "",
    }
    if isinstance(user_session, dict):
        db_user = None
        if user_session.get("id") is not None:
            try:
                db_user = get_user_by_id(user_session["id"])
            except Exception:
                db_user = None
        source = db_user or user_session
        checkout_defaults = {
            "nombre": source.get("nombre_usuario") or source.get("nombre") or "",
            "telefono": source.get("telefono") or "",
            "correo": source.get("email") or "",
            "direccion": source.get("direccion_entrega") or source.get("ciudad") or "",
        }

    return render_template(
        "cart.html",
        items=items,
        subtotal=pricing["subtotal"],
        discount_amount=pricing["discount_amount"],
        discount_percent=pricing["discount_percent"],
        vip_discount_amount=pricing["vip_discount_amount"],
        coupon_code=pricing["coupon_code"],
        coupon_percent=pricing["coupon_percent"],
        coupon_discount_amount=pricing["coupon_discount_amount"],
        coupon_category_name=pricing["coupon_category_name"],
        is_vip=pricing["is_vip"],
        total=pricing["total"],
        checkout_defaults=checkout_defaults,
        cart_count=cart_count(cart_data),
        checkout_token=session.get("checkout_token", ""),
    )


@shop.post("/carrito/cupon")
def apply_coupon():
    action = request.form.get("action", "apply").strip()
    if action == "remove":
        session.pop("applied_coupon", None)
        flash("Cupón promocional retirado del carrito.", "success")
        return redirect(url_for("shop.cart"))

    codigo = request.form.get("codigo", "").strip().upper()
    if not codigo:
        flash("Ingresa un código de cupón válido.", "error")
        return redirect(url_for("shop.cart"))

    coupon = catalog.get_coupon_by_code(codigo)
    if not coupon:
        flash(f"El cupón '{codigo}' no existe o se encuentra inactivo.", "error")
        return redirect(url_for("shop.cart"))

    cart_data = get_session_cart(session)
    items, _subtotal = cart_summary(cart_data)
    target_cat = coupon.get("id_main_cat")
    if target_cat not in (None, "", 0, "0"):
        has_matching = any(
            str(getattr(item.get("product"), "id_main_cat", "")) == str(target_cat)
            for item in items
        )
        if not has_matching:
            cat_label = coupon.get("categoria_nombre") or f"categoría #{target_cat}"
            flash(
                f"El cupón '{codigo}' aplica exclusivamente para productos de '{cat_label}'.",
                "error",
            )
            return redirect(url_for("shop.cart"))

    session["applied_coupon"] = coupon["codigo"]
    flash(
        f"¡Cupón '{coupon['codigo']}' ({int(coupon['porcentaje_descuento'])}% Dto.) aplicado con éxito!",
        "success",
    )
    return redirect(url_for("shop.cart"))


@shop.post("/pedidos")
def create_order():
    checkout_token = request.form.get("checkout_token", "")
    expected_token = session.get("checkout_token", "")
    if (
        not isinstance(checkout_token, str)
        or not isinstance(expected_token, str)
        or not secrets.compare_digest(checkout_token, expected_token)
    ):
        abort(400, description="La sesión de compra venció. Actualiza el carrito e inténtalo de nuevo.")

    customer_name = request.form.get("nombre", "").strip()
    phone = request.form.get("telefono", "").strip()
    email = request.form.get("correo", "").strip()
    delivery_address = request.form.get("direccion", "").strip()
    notes = request.form.get("notas", "").strip()

    if not customer_name or len(customer_name) > 100:
        flash("Ingresa tu nombre (máximo 100 caracteres).", "error")
        return redirect(url_for("shop.cart"))
    if (
        len(phone) > 24
        or not re.fullmatch(r"[0-9+().\s-]+", phone)
        or not 7 <= len(re.sub(r"\D", "", phone)) <= 15
    ):
        flash("Ingresa un número de WhatsApp válido con indicativo de país.", "error")
        return redirect(url_for("shop.cart"))
    if email and (
        len(email) > 254
        or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
    ):
        flash("Revisa el formato del correo electrónico.", "error")
        return redirect(url_for("shop.cart"))
    if len(delivery_address) > 250 or len(notes) > 500:
        flash("La dirección admite 250 caracteres y las notas 500.", "error")
        return redirect(url_for("shop.cart"))

    cart_data = get_session_cart(session)
    items, _total = cart_summary(cart_data)
    save_session_cart(session, cart_data)
    if not items:
        flash("Tu carrito está vacío; agrega productos antes de crear un pedido.", "error")
        return redirect(url_for("shop.cart"))
    if any(item["quantity"] > item["product"].stock for item in items):
        flash("La cantidad de un producto supera el inventario actual. Actualiza el carrito.", "error")
        return redirect(url_for("shop.cart"))

    rate = Decimal(str(current_app.config["USD_TO_COP_RATE"]))
    discount_rate = get_vip_discount_rate(session.get("user"))
    applied_code = session.get("applied_coupon", "")
    active_coupon = catalog.get_coupon_by_code(applied_code) if applied_code else None
    coupon_rate = Decimal("0.00")
    coupon_cat_id = None
    if active_coupon and active_coupon.get("activo", 1):
        coupon_rate = Decimal(str(active_coupon.get("porcentaje_descuento", 0))) / Decimal("100")
        coupon_cat_id = active_coupon.get("id_main_cat")

    order_lines = []
    for item in items:
        product = item["product"]
        item_coupon_rate = Decimal("0.00")
        if coupon_rate > Decimal("0.00"):
            if coupon_cat_id in (None, "", 0, "0") or str(getattr(product, "id_main_cat", "")) == str(coupon_cat_id):
                item_coupon_rate = coupon_rate
        combined_rate = min(Decimal("0.90"), discount_rate + item_coupon_rate)
        price_multiplier = Decimal("1.00") - combined_rate
        unit_price_cop = int(
            (product.precio * rate * price_multiplier).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        line_total_cop = int(
            (item["subtotal"] * rate * price_multiplier).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        order_lines.append((
            product.id_producto,
            product.nombre,
            item["quantity"],
            unit_price_cop,
            line_total_cop,
        ))
    total_cop = sum(line[4] for line in order_lines)

    connection = get_db()
    try:
        connection.execute("BEGIN IMMEDIATE")
        previous = connection.execute(
            "SELECT order_number FROM orders WHERE checkout_token = ?",
            (checkout_token,),
        ).fetchone()
        if previous:
            order_number = previous["order_number"]
        else:
            user_session = session.get("user") or {}
            raw_user_id = user_session.get("id") if isinstance(user_session, dict) else None
            resolved_user_id = None
            if isinstance(raw_user_id, int) and not isinstance(raw_user_id, bool):
                existing_user = connection.execute(
                    "SELECT id FROM usuarios WHERE id = ?", (raw_user_id,)
                ).fetchone()
                if existing_user:
                    resolved_user_id = existing_user["id"]
            elif isinstance(raw_user_id, str) and raw_user_id.isdigit():
                existing_user = connection.execute(
                    "SELECT id FROM usuarios WHERE id = ?", (int(raw_user_id),)
                ).fetchone()
                if existing_user:
                    resolved_user_id = existing_user["id"]

            order_number = (
                f"LP-{datetime.now(timezone.utc):%Y%m%d}-"
                f"{secrets.token_hex(4).upper()}"
            )
            cursor = connection.execute(
                """
                INSERT INTO orders (
                    user_id, order_number, checkout_token, customer_name, phone, email,
                    delivery_address, notes, total_cop
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    resolved_user_id,
                    order_number,
                    checkout_token,
                    customer_name,
                    phone,
                    email,
                    delivery_address,
                    notes,
                    total_cop,
                ),
            )
            connection.executemany(
                """
                INSERT INTO order_items (
                    order_id, product_id, product_name, quantity,
                    unit_price_cop, line_total_cop
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (cursor.lastrowid, *line)
                    for line in order_lines
                ],
            )
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise

    save_session_cart(session, {})
    session["last_order_number"] = order_number
    session.pop("checkout_token", None)
    session.pop("applied_coupon", None)
    return redirect(url_for("shop.order_confirmation"))


@shop.get("/pedido/confirmacion")
def order_confirmation():
    order_number = session.get("last_order_number")
    if not isinstance(order_number, str):
        return redirect(url_for("shop.cart"))
    connection = get_db()
    order = connection.execute(
        "SELECT * FROM orders WHERE order_number = ?", (order_number,)
    ).fetchone()
    if not order:
        session.pop("last_order_number", None)
        return redirect(url_for("shop.cart"))
    items = connection.execute(
        """
        SELECT product_id, product_name, quantity, unit_price_cop, line_total_cop
        FROM order_items WHERE order_id = ? ORDER BY id
        """,
        (order["id"],),
    ).fetchall()
    message = (
        f"Hola, quiero confirmar el pedido {order['order_number']} "
        f"por ${order['total_cop']:,} COP."
    )
    whatsapp_url = (
        "https://wa.me/573145971304?text="
        + quote(message, safe="")
    )
    return render_template(
        "order_confirmation.html",
        order=order,
        items=items,
        whatsapp_url=whatsapp_url,
        cart_count=cart_count(get_session_cart(session)),
    )


@shop.get("/mis-pedidos")
@login_required
def my_orders():
    user_session = session.get("user") or {}
    user_id = user_session.get("id")
    connection = get_db()
    orders_rows = connection.execute(
        """
        SELECT id, order_number, status, customer_name, phone, email,
               delivery_address, notes, total_cop, created_at
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (user_id,),
    ).fetchall()

    status_labels = {
        "pending_confirmation": "Pendiente de confirmación",
        "confirmed": "Confirmado",
        "cancelled": "Cancelado",
    }
    orders_data = []
    for order_row in orders_rows:
        items_rows = connection.execute(
            """
            SELECT product_id, product_name, quantity, unit_price_cop, line_total_cop
            FROM order_items
            WHERE order_id = ?
            ORDER BY id
            """,
            (order_row["id"],),
        ).fetchall()
        orders_data.append({
            "order": order_row,
            "status_label": status_labels.get(
                order_row["status"], order_row["status"]
            ),
            "lines": items_rows,
        })

    return render_template(
        "my_orders.html",
        orders=orders_data,
        cart_count=cart_count(get_session_cart(session)),
    )