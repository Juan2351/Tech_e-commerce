"""
Modelo de Marca
Gestiona operaciones SQL sobre la tabla marca.
"""

from models.database import query

class MarcaModel:
    @staticmethod
    def find_all_with_count():
        sql = """
            SELECT
                m.id_marca,
                m.nombre,
                COUNT(p.id_producto) AS total_productos
            FROM marca m
            LEFT JOIN producto p ON m.id_marca = p.id_marca
            GROUP BY m.id_marca, m.nombre
            ORDER BY m.nombre ASC
        """
        return query(sql)

    @staticmethod
    def find_by_name(nombre):
        sql = "SELECT id_marca, nombre FROM marca WHERE nombre = %s"
        return query(sql, [nombre], fetchone=True)
