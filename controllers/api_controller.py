from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, session

from models import catalog
from models.database import DatabaseConfigurationError, query_one
from services import cart_service

api = Blueprint("api", __name__, url_prefix="/api/v1")


@api.get("/salud")
def database_health():
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
    items, total = cart_service.cart_summary(cart)
    session["cart"] = cart
    return jsonify({
        "data": {
            "items": [
                {
                    "producto": item["product"].to_dict(current_rate()),
                    "cantidad": item["quantity"],
                    "subtotal": int(
                        (item["subtotal"] * current_rate()).quantize(
                            Decimal("1"), rounding=ROUND_HALF_UP
                        )
                    ),
                }
                for item in items
            ],
            "total": int(
                (total * current_rate()).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
            ),
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
