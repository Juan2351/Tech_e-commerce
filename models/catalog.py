from typing import Any, Dict, List, Optional
from flask import current_app, has_app_context

from models.database import get_db, query_all, query_one
from models.entities import Product
from models.firebase_db import FirebaseDB


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


def is_firebase_active() -> bool:
    try:
        if current_app.config.get("TESTING"):
            # En entorno de pruebas unitarias, usar SQLite salvo que se pida explícitamente firebase
            return current_app.config.get("DATABASE_BACKEND") == "firebase"
        backend = current_app.config.get("DATABASE_BACKEND", "sqlite")
        return backend.lower() == "firebase"
    except RuntimeError:
        return False


def fetch_categories() -> List[Dict[str, Any]]:
    if is_firebase_active():
        try:
            return FirebaseDB.get_categories()
        except Exception:
            pass  # Fallback a SQLite si falla la conexión
    return query_all(
        """
        SELECT id_main_cat, nombre
        FROM categoria_principal
        ORDER BY nombre
        """
    )


def fetch_subcategories(main_category_id: Optional[int] = None) -> List[Dict[str, Any]]:
    if is_firebase_active():
        try:
            return FirebaseDB.get_subcategories(main_category_id)
        except Exception:
            pass
    sql = """
        SELECT id_subcat, id_main_cat, nombre
        FROM subcategoria
    """
    params = ()
    if main_category_id is not None:
        sql += " WHERE id_main_cat = ?"
        params = (main_category_id,)
    sql += " ORDER BY nombre"
    return query_all(sql, params)


def fetch_products(
    category_id: Optional[int] = None,
    subcategory_id: Optional[int] = None,
    search: Optional[str] = None,
    sort: str = "featured",
) -> List[Product]:
    if is_firebase_active():
        try:
            products_dict = FirebaseDB.get_all_products_raw()
            items = list(products_dict.values())

            if category_id is not None:
                items = [p for p in items if str(p.get("id_main_cat")) == str(category_id)]
            if subcategory_id is not None:
                items = [p for p in items if str(p.get("id_subcat")) == str(subcategory_id)]
            if search:
                query = search.strip().lower()
                items = [
                    p for p in items
                    if query in p.get("nombre", "").lower()
                    or query in p.get("descripcion", "").lower()
                    or query in p.get("marca", "").lower()
                ]

            if sort == "price_asc":
                items.sort(key=lambda p: float(p.get("precio", 0)))
            elif sort == "price_desc":
                items.sort(key=lambda p: float(p.get("precio", 0)), reverse=True)
            elif sort == "rating_desc":
                items.sort(
                    key=lambda p: (float(p.get("rating", 0)), int(p.get("reviews_count", 0))),
                    reverse=True,
                )
            else:  # featured
                items.sort(key=lambda p: str(p.get("id_producto", "")))

            return [Product.from_row(item) for item in items]
        except Exception:
            pass  # Fallback a SQLite si es necesario

    sql = PRODUCT_SELECT + " WHERE 1 = 1"
    params = []
    if category_id is not None:
        sql += " AND c.id_main_cat = ?"
        params.append(category_id)
    if subcategory_id is not None:
        sql += " AND p.id_subcat = ?"
        params.append(subcategory_id)
    if search:
        sql += " AND (p.nombre LIKE ? OR p.descripcion LIKE ? OR m.nombre LIKE ?)"
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


def fetch_top_products(limit: int = 8) -> List[Product]:
    """Obtiene los productos con mayor calificación y reseñas para la Landing Page."""
    if is_firebase_active():
        try:
            products_dict = FirebaseDB.get_all_products_raw()
            items = list(products_dict.values())
            # Ordenar por rating y número de reseñas
            items.sort(
                key=lambda p: (float(p.get("rating", 0)), int(p.get("reviews_count", 0))),
                reverse=True,
            )
            return [Product.from_row(item) for item in items[:limit]]
        except Exception:
            pass

    sql = PRODUCT_SELECT + " ORDER BY p.rating DESC, p.reviews_count DESC LIMIT ?"
    rows = query_all(sql, (limit,))
    return [Product.from_row(row) for row in rows]


def fetch_product(product_id: str) -> Optional[Product]:
    if is_firebase_active():
        try:
            data = FirebaseDB.get_product(product_id)
            if data:
                return Product.from_row(data)
            return None
        except Exception:
            pass

    row = query_one(
        PRODUCT_SELECT + " WHERE p.id_producto = ?",
        (product_id,),
    )
    return Product.from_row(row) if row else None


def fetch_products_by_ids(product_ids: List[str]) -> List[Product]:
    if not product_ids:
        return []
    if is_firebase_active():
        try:
            products_dict = FirebaseDB.get_all_products_raw()
            selected = [
                Product.from_row(products_dict[pid])
                for pid in product_ids
                if pid in products_dict
            ]
            return selected
        except Exception:
            pass

    placeholders = ", ".join(["?"] * len(product_ids))
    rows = query_all(
        PRODUCT_SELECT + f" WHERE p.id_producto IN ({placeholders})",
        tuple(product_ids),
    )
    return [Product.from_row(row) for row in rows]


# -------------------------------------------------------------
# Funciones Administrativas (CRUD y Estadísticas)
# -------------------------------------------------------------
def save_product(product_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Crea o actualiza un producto en SQLite o Firebase según el backend activo."""
    if is_firebase_active():
        return FirebaseDB.save_product(product_dict)

    connection = get_db()
    brand_name = (product_dict.get("marca") or "LePetit").strip()
    brand_row = connection.execute(
        "SELECT id_marca FROM marca WHERE nombre = ?", (brand_name,)
    ).fetchone()
    if brand_row:
        brand_id = brand_row["id_marca"]
    else:
        cursor = connection.execute(
            "INSERT INTO marca (nombre) VALUES (?)", (brand_name,)
        )
        brand_id = cursor.lastrowid

    subcat_id = int(product_dict.get("id_subcat", 1))
    connection.execute(
        """
        INSERT INTO producto (
            id_producto, nombre, descripcion, precio, rating,
            reviews_count, stock, url, image_url, id_marca, id_subcat
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id_producto) DO UPDATE SET
            nombre = excluded.nombre,
            descripcion = excluded.descripcion,
            precio = excluded.precio,
            rating = excluded.rating,
            reviews_count = excluded.reviews_count,
            stock = excluded.stock,
            url = excluded.url,
            image_url = excluded.image_url,
            id_marca = excluded.id_marca,
            id_subcat = excluded.id_subcat
        """,
        (
            str(product_dict["id_producto"]).strip(),
            str(product_dict["nombre"]).strip(),
            str(product_dict.get("descripcion") or "").strip(),
            str(product_dict.get("precio", 0)),
            str(product_dict.get("rating", 4.5)),
            int(product_dict.get("reviews_count", 0)),
            int(product_dict.get("stock", 0)),
            str(product_dict.get("url") or "").strip(),
            str(product_dict.get("image_url") or "").strip(),
            brand_id,
            subcat_id,
        ),
    )
    connection.commit()
    return product_dict


def delete_product(product_id: str) -> bool:
    """Elimina un producto en SQLite o Firebase según el backend activo."""
    if is_firebase_active():
        return FirebaseDB.delete_product(product_id)

    connection = get_db()
    connection.execute("DELETE FROM producto WHERE id_producto = ?", (product_id,))
    connection.commit()
    return True


def save_category(category_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Crea o actualiza una categoría en SQLite o Firebase según el backend activo."""
    if is_firebase_active():
        return FirebaseDB.save_category(category_dict)

    connection = get_db()
    cat_id = int(category_dict["id_main_cat"])
    nombre = str(category_dict["nombre"]).strip()
    connection.execute(
        """
        INSERT INTO categoria_principal (id_main_cat, nombre)
        VALUES (?, ?)
        ON CONFLICT(id_main_cat) DO UPDATE SET nombre = excluded.nombre
        """,
        (cat_id, nombre),
    )
    connection.commit()
    return category_dict


def delete_category(category_id: int) -> bool:
    """Elimina una categoría en SQLite o Firebase según el backend activo."""
    if is_firebase_active():
        return FirebaseDB.delete_category(category_id)

    connection = get_db()
    connection.execute(
        "DELETE FROM categoria_principal WHERE id_main_cat = ?", (int(category_id),)
    )
    connection.commit()
    return True


def fetch_dashboard_stats() -> Dict[str, Any]:
    """Calcula métricas clave del catálogo e inventario para el dashboard."""
    if is_firebase_active():
        products = FirebaseDB.get_all_products_raw()
        categories = FirebaseDB.get_categories()
        users = FirebaseDB.get_users()

        total_products = len(products)
        total_categories = len(categories)
        total_clients = sum(
            1 for u in users if (u.get("rol") or u.get("role")) != "admin"
        )
        total_stock = sum(int(p.get("stock", 0)) for p in products.values())
        total_value_usd = sum(
            float(p.get("precio", 0)) * int(p.get("stock", 0))
            for p in products.values()
        )
        low_stock_count = sum(
            1 for p in products.values() if int(p.get("stock", 0)) < 15
        )

        return {
            "total_products": total_products,
            "total_categories": total_categories,
            "total_clients": total_clients,
            "total_stock": total_stock,
            "total_value_usd": round(total_value_usd, 2),
            "low_stock_count": low_stock_count,
        }

    product_stats = query_one(
        """
        SELECT
            COUNT(*) AS total_products,
            COALESCE(SUM(stock), 0) AS total_stock,
            COALESCE(SUM(precio * stock), 0) AS total_value_usd,
            COALESCE(SUM(CASE WHEN stock < 15 THEN 1 ELSE 0 END), 0)
                AS low_stock_count
        FROM producto
        """
    )
    category_stats = query_one(
        "SELECT COUNT(*) AS total_categories FROM categoria_principal"
    )
    if has_app_context():
        client_row = get_db().execute(
            "SELECT COUNT(*) AS total_clients FROM usuarios WHERE rol != 'admin'"
        ).fetchone()
        total_clients = client_row["total_clients"] if client_row else 0
    else:
        users = FirebaseDB.get_users()
        total_clients = sum(
            1 for user in users if (user.get("rol") or user.get("role")) != "admin"
        )
    return {
        "total_products": product_stats["total_products"],
        "total_categories": category_stats["total_categories"],
        "total_clients": total_clients,
        "total_stock": product_stats["total_stock"],
        "total_value_usd": round(float(product_stats["total_value_usd"]), 2),
        "low_stock_count": product_stats["low_stock_count"],
    }
