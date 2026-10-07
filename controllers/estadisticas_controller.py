"""
Controlador de Estadisticas
Rutas HTTP bajo el prefijo /api/v1/estadisticas
"""

from flask import Blueprint, jsonify
from services.catalogo_service import CatalogoService

estadisticas_bp = Blueprint("estadisticas", __name__, url_prefix="/api/v1/estadisticas")

@estadisticas_bp.route("", methods=["GET"])
def get_estadisticas():
    """Resumen de indicadores generales del catalogo."""
    try:
        stats = CatalogoService.obtener_estadisticas()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": f"Error al calcular estadisticas: {str(e)}"}), 500
