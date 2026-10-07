"""
Modelo de Estadisticas
Calcula indicadores de negocio globales del catalogo.
"""

from api.models.database import query

class EstadisticasModel:
    @staticmethod
    def get_summary():
        sql = """
            SELECT
                COUNT(p.id_producto)           AS total_productos,
                COUNT(DISTINCT p.id_marca)     AS total_marcas,
                COUNT(DISTINCT s.id_main_cat)  AS total_categorias,
                ROUND(AVG(p.precio), 2)        AS precio_promedio_usd,
                ROUND(AVG(p.rating), 2)        AS rating_promedio
            FROM producto p
            LEFT JOIN subcategoria s ON p.id_subcat = s.id_subcat
        """
        return query(sql, fetchone=True)
