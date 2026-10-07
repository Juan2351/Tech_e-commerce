"""
Controlador de Marcas
Rutas HTTP bajo el prefijo /api/v1/marcas
"""

from flask import Blueprint, jsonify
from services.catalogo_service import CatalogoService

marcas_bp = Blueprint("marcas", __name__, url_prefix="/api/v1/marcas")

@marcas_bp.route("", methods=["GET"])
def get_marcas():
    """Listar todas las marcas con conteo de productos."""
    try:
        marcas = CatalogoService.listar_marcas()
        return jsonify(marcas), 200
    except Exception as e:
        return jsonify({"error": f"Error al consultar marcas: {str(e)}"}), 500
