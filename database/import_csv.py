"""
Script de Importacion de Datos CSV a MySQL
Proyecto: Amazon Tech Products E-commerce
Base de datos: ecommerce_db
"""

import os
import csv
import sys
from decimal import Decimal
from pathlib import Path
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Cargar variables de entorno desde api/.env si existe
env_path = Path(__file__).resolve().parent.parent / "api" / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "ecommerce_db"),
    "charset":  "utf8mb4",
}

CSV_FILENAME = "amazon_tech_products_ecommerceGKALI.csv"
CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "conjunto_datos"
    / CSV_FILENAME
)


def clean_price(val):
    """Limpia y convierte cadenas de precio a float."""
    if val is None:
        return 0.0
    text = str(val).replace("$", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return 0.0


def clean_decimal(val, default="0.00"):
    """Limpia y convierte a Decimal para campos de precision fija."""
    try:
        clean = str(val).strip()
        return Decimal(clean) if clean else Decimal(default)
    except Exception:
        return Decimal(default)


def clean_int(val, default=0):
    """Limpia y convierte a entero."""
    try:
        clean = str(val).strip()
        return int(float(clean)) if clean else default
    except Exception:
        return default


def importar():
    """Ejecuta el proceso ETL de importacion desde CSV a MySQL."""
    if not CSV_PATH.exists():
        print(f"Error: No se encontro el archivo CSV en {CSV_PATH}")
        sys.exit(1)

    print(f"Iniciando importacion a MySQL...")
    print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']} | Base de datos: {DB_CONFIG['database']}")

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()
    except Error as err:
        print(f"Error de conexion a MySQL: {err}")
        print("Asegurate de que el servicio MySQL este en ejecucion y que las credenciales en api/.env sean correctas.")
        sys.exit(1)

    try:
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        total_filas = len(rows)
        print(f"Registros leidos del CSV: {total_filas}")

        # 1. Insertar marcas unicas
        marcas = sorted(set(r["brand_name"].strip() for r in rows if r.get("brand_name", "").strip()))
        for marca in marcas:
            cur.execute(
                "INSERT INTO marca (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
                (marca,)
            )
        conn.commit()
        print(f"Marcas procesadas: {len(marcas)}")

        # 2. Insertar categorias principales unicas
        main_cats = sorted(set(r["main_category"].strip() for r in rows if r.get("main_category", "").strip()))
        for cat in main_cats:
            cur.execute(
                "INSERT INTO categoria_principal (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)",
                (cat,)
            )
        conn.commit()
        print(f"Categorias principales procesadas: {len(main_cats)}")

        # 3. Mapear categorias principales a su ID
        cur.execute("SELECT nombre, id_main_cat FROM categoria_principal")
        cat_map = {name: cid for name, cid in cur.fetchall()}

        # 4. Insertar subcategorias unicas
        subcat_pairs = set(
            (r["subcategory"].strip(), r["main_category"].strip())
            for r in rows
            if r.get("subcategory", "").strip() and r.get("main_category", "").strip()
        )
        for subcat_name, maincat_name in sorted(subcat_pairs):
            main_id = cat_map.get(maincat_name)
            if main_id:
                cur.execute(
                    """INSERT INTO subcategoria (id_main_cat, nombre)
                       VALUES (%s, %s)
                       ON DUPLICATE KEY UPDATE id_main_cat = VALUES(id_main_cat)""",
                    (main_id, subcat_name)
                )
        conn.commit()
        print(f"Subcategorias procesadas: {len(subcat_pairs)}")

        # 5. Mapeos de marcas y subcategorias para asociacion rapida
        cur.execute("SELECT nombre, id_marca FROM marca")
        marca_map = {name: mid for name, mid in cur.fetchall()}

        cur.execute("""
            SELECT s.nombre, c.nombre, s.id_subcat
            FROM subcategoria s
            JOIN categoria_principal c ON s.id_main_cat = c.id_main_cat
        """)
        subcat_map = {(s_name, c_name): sid for s_name, c_name, sid in cur.fetchall()}

        # 6. Insertar productos en lotes
        insert_sql = """
            INSERT INTO producto (
                id_producto, descripcion, precio, rating, reviews_count,
                stock, url, image_url, id_marca, id_subcat
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                descripcion = VALUES(descripcion),
                precio = VALUES(precio),
                rating = VALUES(rating),
                reviews_count = VALUES(reviews_count),
                stock = VALUES(stock),
                url = VALUES(url),
                image_url = VALUES(image_url),
                id_marca = VALUES(id_marca),
                id_subcat = VALUES(id_subcat)
        """

        batch = []
        batch_size = 500
        total_insertados = 0

        for r in rows:
            prod_id = r["id"].strip()
            desc = r["product_description"].strip()
            precio_val = clean_price(r.get("price_numeric") or r.get("price"))
            rating_val = clean_decimal(r.get("rating"), default="0.00")
            reviews_val = clean_int(r.get("reviews_count"), default=0)
            stock_val = clean_int(r.get("stock"), default=0)
            url_val = r.get("url", "").strip()[:500]
            img_val = r.get("image_url", "").strip()[:500]

            marca_id = marca_map.get(r.get("brand_name", "").strip())
            subcat_id = subcat_map.get((r.get("subcategory", "").strip(), r.get("main_category", "").strip()))

            batch.append((
                prod_id, desc, Decimal(str(round(precio_val, 2))),
                rating_val, reviews_val, stock_val, url_val, img_val,
                marca_id, subcat_id
            ))

            if len(batch) >= batch_size:
                cur.executemany(insert_sql, batch)
                conn.commit()
                total_insertados += len(batch)
                print(f"Progreso: {total_insertados}/{total_filas} productos procesados...")
                batch = []

        if batch:
            cur.executemany(insert_sql, batch)
            conn.commit()
            total_insertados += len(batch)

        print(f"\nImportacion finalizada con exito.")
        print(f"Total productos en base de datos: {total_insertados}")

    except Exception as e:
        conn.rollback()
        print(f"Error durante la importacion: {e}")
        raise e
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    importar()
