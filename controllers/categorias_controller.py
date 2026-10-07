"""
Controlador de Categorias
Rutas HTTP bajo el prefijo /api/v1/categorias
"""

from flask import Blueprint, jsonify
from services.catalogo_service import CatalogoService

categorias_bp = Blueprint("categorias", __name__, url_prefix="/api/v1/categorias")

@categorias_bp.route("", methods=["GET"])
def get_categorias():
    """Listar categorias con sus subcategorias anidadas."""
    try:
        cats = CatalogoService.listar_categorias()
        return jsonify(cats), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar categorias: {str(e)}"}), 500
