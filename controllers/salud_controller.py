"""
Controlador de Salud y Diagnostico
Rutas HTTP bajo el prefijo /api/v1/salud
"""

from flask import Blueprint, jsonify
from models.database import get_engine, get_mysql_error, query

salud_bp = Blueprint("salud", __name__, url_prefix="/api/v1/salud")

@salud_bp.route("", methods=["GET"])
def check_salud():
    """Verifica la conectividad de la API y de la base de datos."""
    try:
        motor = get_engine()
        check = query("SELECT 1 AS ok", fetchone=True)
        conteo = query("SELECT COUNT(*) AS total FROM producto", fetchone=True)
        return jsonify({
            "estado": "operativo",
            "base_de_datos": {
                "conectada": bool(check),
                "motor": motor,
                "mysql_disponible": motor == "MySQL",
                "detalle": get_mysql_error() if motor != "MySQL" else None,
                "total_productos": conteo["total"] if conteo else 0
            }
        }), 200
    except Exception as e:
        return jsonify({
            "estado": "error",
            "detalle": str(e)
        }), 503
