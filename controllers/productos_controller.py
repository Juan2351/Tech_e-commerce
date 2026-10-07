"""
Controlador de Productos
Rutas HTTP bajo el prefijo /api/v1/productos
"""

from flask import Blueprint, request, jsonify
from services.producto_service import ProductoService

productos_bp = Blueprint("productos", __name__, url_prefix="/api/v1/productos")

@productos_bp.route("", methods=["GET"])
def get_productos():
    """Listar productos con paginacion, filtros y ordenamiento."""
    try:
        resultado = ProductoService.listar_productos(request.args)
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": f"Error interno al consultar productos: {str(e)}"}), 500


@productos_bp.route("/<string:id_producto>", methods=["GET"])
def get_producto_por_id(id_producto):
    """Obtener detalle de un producto por ID."""
    try:
        producto, error = ProductoService.obtener_por_id(id_producto)
        if error:
            return jsonify({"error": error}), 404
        return jsonify(producto), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@productos_bp.route("", methods=["POST"])
def crear_producto():
    """Registrar un nuevo producto."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de peticion JSON requerido"}), 400

    try:
        nuevo_prod, error = ProductoService.crear_producto(data)
        if error:
            return jsonify({"error": error}), 400
        return jsonify(nuevo_prod), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@productos_bp.route("/<string:id_producto>", methods=["PUT"])
def actualizar_producto(id_producto):
    """Actualizar datos de un producto existente."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Cuerpo de peticion JSON requerido"}), 400

    try:
        actualizado, error = ProductoService.actualizar_producto(id_producto, data)
        if error:
            codigo = 404 if error == "Producto no encontrado" else 400
            return jsonify({"error": error}), codigo
        return jsonify(actualizado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@productos_bp.route("/<string:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    """Eliminar un producto por ID."""
    try:
        eliminado, error = ProductoService.eliminar_producto(id_producto)
        if error:
            return jsonify({"error": error}), 404
        return jsonify({"mensaje": f"Producto '{id_producto}' eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
