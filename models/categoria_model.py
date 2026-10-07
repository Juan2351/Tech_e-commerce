"""
Modelo de Categoria y Subcategoria
Gestiona operaciones SQL sobre categorias y subcategorias.
"""

from models.database import query

class CategoriaModel:
    @staticmethod
    def find_all_nested():
        sql = """
            SELECT
                c.id_main_cat AS id_categoria,
                c.nombre      AS categoria,
                s.id_subcat   AS id_subcategoria,
                s.nombre      AS subcategoria,
                COUNT(p.id_producto) AS total_productos
            FROM categoria_principal c
            JOIN subcategoria s ON c.id_main_cat = s.id_main_cat
            LEFT JOIN producto p ON s.id_subcat = p.id_subcat
            GROUP BY c.id_main_cat, c.nombre, s.id_subcat, s.nombre
            ORDER BY c.nombre ASC, s.nombre ASC
        """
        rows = query(sql)

        cats = {}
        for row in rows:
            cid = row["id_categoria"]
            if cid not in cats:
                cats[cid] = {
                    "id_categoria": cid,
                    "nombre": row["categoria"],
                    "subcategorias": []
                }
            cats[cid]["subcategorias"].append({
                "id_subcategoria": row["id_subcategoria"],
                "nombre": row["subcategoria"],
                "total_productos": row["total_productos"]
            })

        return list(cats.values())
