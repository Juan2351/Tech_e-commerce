import csv
import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path

from models.database_errors import DatabaseConfigurationError


REQUIRED_COLUMNS = {
    "product_description",
    "price_numeric",
    "rating",
    "reviews_count",
    "url",
    "brand_name",
    "id",
    "main_category",
    "subcategory",
    "image_url",
    "stock",
}


def _required_text(row, column, row_number):
    value = (row.get(column) or "").strip()
    if not value:
        raise DatabaseConfigurationError(
            f"El catálogo CSV tiene vacío el campo {column} en la fila {row_number}."
        )
    return value


def _import_catalog(connection, csv_path):
    path = Path(csv_path)
    if not path.is_file():
        raise DatabaseConfigurationError(
            f"No se encontró el catálogo CSV requerido: {path}"
        )

    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames or ())
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise DatabaseConfigurationError(
                f"Al catálogo CSV le faltan las columnas requeridas: {missing}."
            )

        brands = {
            row["nombre"]: row["id_marca"]
            for row in connection.execute("SELECT id_marca, nombre FROM marca")
        }
        categories = {
            row["nombre"]: row["id_main_cat"]
            for row in connection.execute(
                "SELECT id_main_cat, nombre FROM categoria_principal"
            )
        }
        subcategories = {
            (row["id_main_cat"], row["nombre"]): row["id_subcat"]
            for row in connection.execute(
                "SELECT id_subcat, id_main_cat, nombre FROM subcategoria"
            )
        }
        products = []

        for row_number, row in enumerate(reader, start=2):
            try:
                name = _required_text(row, "product_description", row_number)
                brand_name = _required_text(row, "brand_name", row_number)
                category_name = _required_text(row, "main_category", row_number)
                subcategory_name = _required_text(row, "subcategory", row_number)
                product_id = _required_text(row, "id", row_number)
                price = Decimal(_required_text(row, "price_numeric", row_number))
                rating = Decimal(_required_text(row, "rating", row_number))
                reviews_count = int(_required_text(row, "reviews_count", row_number))
                stock = int(_required_text(row, "stock", row_number))
            except (InvalidOperation, ValueError) as error:
                raise DatabaseConfigurationError(
                    f"El catálogo CSV tiene un dato numérico inválido en la fila {row_number}."
                ) from error

            if (
                not price.is_finite()
                or not rating.is_finite()
                or price < 0
                or not Decimal("0") <= rating <= Decimal("5")
            ):
                raise DatabaseConfigurationError(
                    f"El catálogo CSV tiene un precio o calificación inválidos en la fila {row_number}."
                )
            if reviews_count < 0 or stock < 0:
                raise DatabaseConfigurationError(
                    f"El catálogo CSV tiene reseñas o existencias inválidas en la fila {row_number}."
                )

            if brand_name not in brands:
                connection.execute(
                    "INSERT INTO marca (nombre) VALUES (?)", (brand_name,)
                )
                brands[brand_name] = connection.execute(
                    "SELECT id_marca FROM marca WHERE nombre = ?", (brand_name,)
                ).fetchone()["id_marca"]

            if category_name not in categories:
                connection.execute(
                    "INSERT INTO categoria_principal (nombre) VALUES (?)",
                    (category_name,),
                )
                categories[category_name] = connection.execute(
                    "SELECT id_main_cat FROM categoria_principal WHERE nombre = ?",
                    (category_name,),
                ).fetchone()["id_main_cat"]

            category_id = categories[category_name]
            subcategory_key = (category_id, subcategory_name)
            if subcategory_key not in subcategories:
                connection.execute(
                    """
                    INSERT INTO subcategoria (id_main_cat, nombre)
                    VALUES (?, ?)
                    """,
                    subcategory_key,
                )
                subcategories[subcategory_key] = connection.execute(
                    """
                    SELECT id_subcat FROM subcategoria
                    WHERE id_main_cat = ? AND nombre = ?
                    """,
                    subcategory_key,
                ).fetchone()["id_subcat"]

            products.append((
                product_id,
                name,
                "",
                str(price),
                str(rating),
                reviews_count,
                stock,
                _required_text(row, "url", row_number),
                _required_text(row, "image_url", row_number),
                brands[brand_name],
                subcategories[subcategory_key],
            ))

        if not products:
            raise DatabaseConfigurationError("El catálogo CSV no contiene productos.")

        connection.executemany(
            """
            INSERT INTO producto (
                id_producto, nombre, descripcion, precio, rating,
                reviews_count, stock, url, image_url, id_marca, id_subcat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            products,
        )


def initialize_database(connection, schema_path, seed_path, csv_path):
    try:
        has_catalog_table = connection.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'producto'
            """
        ).fetchone()
        if not has_catalog_table:
            schema = Path(schema_path).read_text(encoding="utf-8")
            seed = Path(seed_path).read_text(encoding="utf-8")
            connection.executescript(f"{schema}\n{seed}")

        connection.execute("BEGIN IMMEDIATE")
        product_count = connection.execute(
            "SELECT COUNT(*) AS total FROM producto"
        ).fetchone()["total"]
        if not product_count:
            _import_catalog(connection, csv_path)
        connection.commit()
    except sqlite3.IntegrityError as error:
        connection.rollback()
        raise DatabaseConfigurationError(
            "No se pudo importar el catálogo CSV por un conflicto de datos."
        ) from error
    except DatabaseConfigurationError:
        connection.rollback()
        raise
    except (OSError, UnicodeError, csv.Error) as error:
        connection.rollback()
        raise DatabaseConfigurationError(
            "No se pudo leer el esquema, la semilla o el catálogo CSV."
        ) from error
