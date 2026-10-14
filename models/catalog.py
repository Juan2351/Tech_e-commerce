from models.database import query_all, query_one
from models.entities import Product


PRODUCT_SELECT = """
    SELECT
        p.id_producto, p.nombre, p.descripcion, p.precio, p.rating,
        p.reviews_count, p.stock, p.url, p.image_url, p.id_marca,
        p.id_subcat, m.nombre AS marca, s.nombre AS subcategoria,
        c.nombre AS categoria, c.id_main_cat
    FROM producto AS p
    JOIN marca AS m ON m.id_marca = p.id_marca
    JOIN subcategoria AS s ON s.id_subcat = p.id_subcat
    JOIN categoria_principal AS c ON c.id_main_cat = s.id_main_cat
"""


def fetch_categories():
    return query_all(
        """
        SELECT id_main_cat, nombre
        FROM categoria_principal
        ORDER BY nombre
        """
    )


def fetch_subcategories(main_category_id=None):
    sql = """
        SELECT id_subcat, id_main_cat, nombre
        FROM subcategoria
    """
    params = ()
    if main_category_id is not None:
        sql += " WHERE id_main_cat = %s"
        params = (main_category_id,)
    sql += " ORDER BY nombre"
    return query_all(sql, params)


def fetch_products(category_id=None, subcategory_id=None, search=None, sort="featured"):
    sql = PRODUCT_SELECT + " WHERE 1 = 1"
    params = []
    if category_id is not None:
        sql += " AND c.id_main_cat = %s"
        params.append(category_id)
    if subcategory_id is not None:
        sql += " AND p.id_subcat = %s"
        params.append(subcategory_id)
    if search:
        sql += " AND (p.nombre LIKE %s OR p.descripcion LIKE %s OR m.nombre LIKE %s)"
        pattern = f"%{search}%"
        params.extend((pattern, pattern, pattern))

    order_by = {
        "featured": "p.id_producto",
        "price_asc": "p.precio ASC",
        "price_desc": "p.precio DESC",
        "rating_desc": "p.rating DESC, p.reviews_count DESC",
    }
    sql += f" ORDER BY {order_by.get(sort, order_by['featured'])}"
    rows = query_all(sql, tuple(params))
    return [Product.from_row(row) for row in rows]


def fetch_product(product_id):
    row = query_one(
        PRODUCT_SELECT + " WHERE p.id_producto = %s",
        (product_id,),
    )
    return Product.from_row(row) if row else None


def fetch_products_by_ids(product_ids):
    if not product_ids:
        return []
    placeholders = ", ".join(["%s"] * len(product_ids))
    rows = query_all(
        PRODUCT_SELECT + f" WHERE p.id_producto IN ({placeholders})",
        tuple(product_ids),
    )
    return [Product.from_row(row) for row in rows]
