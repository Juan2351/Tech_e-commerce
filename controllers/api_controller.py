from functools import wraps
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, session
from flask_jwt_extended import create_access_token, get_jwt, jwt_required

from models import catalog
from models.auth_model import authenticate_user
from models.database import DatabaseConfigurationError, query_one
from services import cart_service

api = Blueprint("api", __name__, url_prefix="/api/v1")


@api.get("/salud")
def database_health():
    backend = current_app.config.get("DATABASE_BACKEND", "sqlite")
    if not current_app.config.get("TESTING") and backend.lower() == "firebase":
        from models.firebase_db import FirebaseDB
        ok = FirebaseDB.ping()
        if not ok:
            raise DatabaseConfigurationError("No fue posible confirmar la conexión con Firebase.")
        return jsonify({
            "data": {
                "status": "ok",
                "database": "lepetit-e4386 (Firebase RTDB)",
                "engine": "Firebase Realtime Database",
                "connection": True,
                "usd_to_cop_rate": str(current_rate()),
            }
        })

    result = query_one("SELECT 1 AS connection_ok")
    if not result or result["connection_ok"] != 1:
        raise DatabaseConfigurationError(
            "La consulta de verificación no confirmó la conexión SQLite."
        )
    return jsonify({
        "data": {
            "status": "ok",
            "database": Path(current_app.config["DATABASE_PATH"]).name,
            "engine": "SQLite",
            "connection": True,
            "usd_to_cop_rate": str(current_rate()),
        }
    })


def error_response(code, message, status):
    return jsonify({"error": {"code": code, "message": message}}), status


def current_rate():
    return Decimal(str(current_app.config["USD_TO_COP_RATE"]))


def cart_count(cart):
    return sum(
        quantity for quantity in cart.values()
        if isinstance(quantity, int) and not isinstance(quantity, bool) and quantity > 0
    )


def admin_token_required(function):
    @wraps(function)
    @jwt_required()
    def decorated(*args, **kwargs):
        if get_jwt().get("role") != "admin":
            return error_response(
                "forbidden", "Se requieren permisos de administrador.", 403
            )
        return function(*args, **kwargs)
    return decorated


@api.post("/auth/login")
def issue_access_token():
    if not request.is_json:
        return error_response("invalid_content_type", "Envía el contenido como JSON.", 400)
    payload = request.get_json()
    if not isinstance(payload, dict):
        return error_response("invalid_body", "El cuerpo debe ser un objeto JSON.", 400)
    email = payload.get("email")
    password = payload.get("password")
    if not isinstance(email, str) or not email.strip():
        return error_response("invalid_body", "email es obligatorio.", 400)
    if not isinstance(password, str) or not password:
        return error_response("invalid_body", "password es obligatorio.", 400)

    user = authenticate_user(email, password)
    if not user or not user.get("id"):
        return error_response("invalid_credentials", "Credenciales incorrectas.", 401)

    rol = user.get("rol") or user.get("role", "cliente")
    access_token = create_access_token(
        identity=str(user["id"]),
        additional_claims={
            "role": rol,
            "rol": rol,
            "email": user.get("email", ""),
        },
    )
    expires_in = int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds())
    return jsonify({
        "data": {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
        }
    })


@api.get("/admin/dashboard")
@admin_token_required
def get_admin_dashboard():
    return jsonify({"data": catalog.fetch_dashboard_stats()})


def parse_optional_id(value, field_name):
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} debe ser un entero positivo.") from None
    if parsed < 1:
        raise ValueError(f"{field_name} debe ser un entero positivo.")
    return parsed


@api.get("/productos")
def list_products():
    try:
        category_id = parse_optional_id(request.args.get("category_id"), "category_id")
        subcategory_id = parse_optional_id(
            request.args.get("subcategory_id"), "subcategory_id"
        )
        search = request.args.get("q", "").strip()
        if len(search) > 100:
            return error_response("invalid_query", "q no puede superar 100 caracteres.", 400)
        sort = request.args.get("sort", "featured")
        if sort not in {"featured", "price_asc", "price_desc", "rating_desc"}:
            return error_response("invalid_query", "El criterio sort no es válido.", 400)
    except ValueError as error:
        return error_response("invalid_query", str(error), 400)

    products = catalog.fetch_products(category_id, subcategory_id, search, sort)
    rate = current_rate()
    return jsonify({"data": [product.to_dict(rate) for product in products]})


@api.get("/productos/<string:product_id>")
def get_product(product_id):
    product = catalog.fetch_product(product_id)
    if product is None:
        return error_response("not_found", "No existe el producto solicitado.", 404)
    return jsonify({"data": product.to_dict(current_rate())})


@api.get("/categorias")
def list_categories():
    return jsonify({
        "data": [
            {
                **category,
                "subcategorias": catalog.fetch_subcategories(category["id_main_cat"]),
            }
            for category in catalog.fetch_categories()
        ]
    })


@api.get("/carrito")
def get_cart():
    cart = session.get("cart", {})
    items, subtotal = cart_service.cart_summary(cart)
    pricing = cart_service.calculate_cart_totals(subtotal, session.get("user"))
    session["cart"] = cart
    rate = current_rate()
    subtotal_cop = int(
        (pricing["subtotal"] * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    discount_cop = int(
        (pricing["discount_amount"] * rate).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )
    total_cop = subtotal_cop - discount_cop
    return jsonify({
        "data": {
            "items": [
                {
                    "producto": item["product"].to_dict(rate),
                    "cantidad": item["quantity"],
                    "subtotal": int(
                        (item["subtotal"] * rate).quantize(
                            Decimal("1"), rounding=ROUND_HALF_UP
                        )
                    ),
                }
                for item in items
            ],
            "subtotal": subtotal_cop,
            "descuento_vip": discount_cop,
            "porcentaje_descuento": pricing["discount_percent"],
            "total": total_cop,
            "moneda": "COP",
        }
    })


@api.post("/carrito/productos")
def add_cart_product():
    if not request.is_json:
        return error_response("invalid_content_type", "Envía el contenido como JSON.", 400)
    payload = request.get_json()
    if not isinstance(payload, dict):
        return error_response("invalid_body", "El cuerpo debe ser un objeto JSON.", 400)
    product_id = payload.get("product_id")
    quantity = payload.get("quantity")
    cart = session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    try:
        product, cart_quantity = cart_service.add_product(cart, product_id, quantity)
    except cart_service.CartProductNotFound as error:
        return error_response("not_found", str(error), 404)
    except cart_service.CartStockError as error:
        return error_response("insufficient_stock", str(error), 409)
    except cart_service.CartError as error:
        return error_response("invalid_body", str(error), 400)

    session["cart"] = cart
    return jsonify({
        "data": {
            "product_id": product.id_producto,
            "quantity": cart_quantity,
            "cart_count": cart_count(cart),
            "message": "Producto agregado al carrito.",
        }
    }), 201


@api.patch("/carrito/productos/<string:product_id>")
def change_cart_product(product_id):
    if not request.is_json:
        return error_response("invalid_content_type", "Envía el contenido como JSON.", 400)
    payload = request.get_json()
    if not isinstance(payload, dict) or "quantity" not in payload:
        return error_response(
            "invalid_body", "El cuerpo debe incluir quantity como entero.", 400
        )
    cart = session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    try:
        cart_service.update_quantity(cart, product_id, payload["quantity"])
    except cart_service.CartProductNotFound as error:
        return error_response("not_found", str(error), 404)
    except cart_service.CartItemNotFound as error:
        return error_response("not_found", str(error), 404)
    except cart_service.CartStockError as error:
        return error_response("insufficient_stock", str(error), 409)
    except cart_service.CartError as error:
        return error_response("invalid_body", str(error), 400)
    session["cart"] = cart
    return jsonify({"data": {"product_id": product_id, "quantity": cart[product_id]}})


@api.delete("/carrito/productos/<string:product_id>")
def delete_cart_product(product_id):
    cart = session.get("cart", {})
    if product_id not in cart:
        return error_response("not_found", "El producto no está en el carrito.", 404)
    del cart[product_id]
    session["cart"] = cart
    return "", 204
