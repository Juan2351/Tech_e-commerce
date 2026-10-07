"""
Modelo de Producto
Gestiona las operaciones CRUD y consultas SQL sobre la tabla producto.
"""

from models.database import query

class ProductoModel:
    @staticmethod
    def find_all(conditions, params, sort_col="p.id_producto ASC", limit=24, offset=0):
        where = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
            SELECT
                p.id_producto,
                p.descripcion,
                m.nombre          AS marca,
                c.nombre          AS categoria,
                s.nombre          AS subcategoria,
                p.precio,
                p.rating,
                p.reviews_count,
                p.url,
                p.image_url,
                p.stock
            FROM producto p
            LEFT JOIN marca m ON p.id_marca = m.id_marca
            LEFT JOIN subcategoria s ON p.id_subcat = s.id_subcat
            LEFT JOIN categoria_principal c ON s.id_main_cat = c.id_main_cat
            WHERE {where}
            ORDER BY {sort_col}
            LIMIT %s OFFSET %s
        """
        return query(sql, params + [limit, offset])

    @staticmethod
    def count(conditions, params):
        where = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
            SELECT COUNT(*) AS total
            FROM producto p
            LEFT JOIN marca m ON p.id_marca = m.id_marca
            LEFT JOIN subcategoria s ON p.id_subcat = s.id_subcat
            LEFT JOIN categoria_principal c ON s.id_main_cat = c.id_main_cat
            WHERE {where}
        """
        res = query(sql, params, fetchone=True)
        return res["total"] if res else 0

    @staticmethod
    def find_by_id(id_producto):
        sql = """
            SELECT
                p.id_producto,
                p.descripcion,
                m.nombre          AS marca,
                c.nombre          AS categoria,
                s.nombre          AS subcategoria,
                p.precio,
                p.rating,
                p.reviews_count,
                p.url,
                p.image_url,
                p.stock,
                p.id_marca,
                p.id_subcat
            FROM producto p
            LEFT JOIN marca m ON p.id_marca = m.id_marca
            LEFT JOIN subcategoria s ON p.id_subcat = s.id_subcat
            LEFT JOIN categoria_principal c ON s.id_main_cat = c.id_main_cat
            WHERE p.id_producto = %s
        """
        return query(sql, [id_producto], fetchone=True)

    @staticmethod
    def create(data):
        sql = """
            INSERT INTO producto (
                id_producto, descripcion, precio, rating, reviews_count,
                stock, url, image_url, id_marca, id_subcat
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = [
            data["id_producto"],
            data["descripcion"],
            data["precio"],
            data.get("rating", 0.0),
            data.get("reviews_count", 0),
            data.get("stock", 0),
            data.get("url", ""),
            data.get("image_url", ""),
            data.get("id_marca"),
            data.get("id_subcat")
        ]
        return query(sql, params, commit=True)

    @staticmethod
    def update(id_producto, fields):
        set_clauses = [f"{col} = %s" for col in fields.keys()]
        sql = f"UPDATE producto SET {', '.join(set_clauses)} WHERE id_producto = %s"
        params = list(fields.values()) + [id_producto]
        return query(sql, params, commit=True)

    @staticmethod
    def delete(id_producto):
        sql = "DELETE FROM producto WHERE id_producto = %s"
        return query(sql, [id_producto], commit=True)
