"""
Script Alternativo de Carga de Datos usando pandas
Carga los datos del CSV a MySQL usando el esquema ecommerce_db.

Uso (ejecutar desde la raiz del proyecto):
    python database/load_data.py

Requiere: pip install pandas mysql-connector-python
o con el entorno virtual: api/.venv/Scripts/python database/load_data.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar credenciales desde api/.env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / "api" / ".env")

import pandas as pd
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "ecommerce_db"),
}

CSV_PATH = BASE_DIR / "conjunto_datos" / "amazon_tech_products_ecommerceGKALI.csv"


def populate_database():
    if not CSV_PATH.exists():
        print(f"Error: No se encontro el CSV en {CSV_PATH}")
        return

    try:
        print("Conectando a MySQL...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print(f"Leyendo CSV desde {CSV_PATH}...")
        df = pd.read_csv(CSV_PATH)

        # 1. Marcas unicas
        print("Insertando marcas...")
        brands = df["brand_name"].dropna().unique()
        cursor.executemany(
            "INSERT IGNORE INTO marca (nombre) VALUES (%s)",
            [(str(b).strip(),) for b in brands]
        )
        conn.commit()

        cursor.execute("SELECT nombre, id_marca FROM marca")
        brand_map = {name: bid for name, bid in cursor.fetchall()}

        # 2. Categorias principales
        print("Insertando categorias principales...")
        main_categories = df["main_category"].dropna().unique()
        cursor.executemany(
            "INSERT IGNORE INTO categoria_principal (nombre) VALUES (%s)",
            [(str(c).strip(),) for c in main_categories]
        )
        conn.commit()

        cursor.execute("SELECT nombre, id_main_cat FROM categoria_principal")
        main_cat_map = {name: cid for name, cid in cursor.fetchall()}

        # 3. Subcategorias con su categoria principal
        print("Insertando subcategorias...")
        subcats_df = df[["main_category", "subcategory"]].dropna().drop_duplicates()
        subcat_data = []
        for _, row in subcats_df.iterrows():
            main_id = main_cat_map.get(str(row["main_category"]).strip())
            sub_name = str(row["subcategory"]).strip()
            if main_id and sub_name:
                subcat_data.append((main_id, sub_name))

        cursor.executemany(
            "INSERT IGNORE INTO subcategoria (id_main_cat, nombre) VALUES (%s, %s)",
            subcat_data
        )
        conn.commit()

        cursor.execute("SELECT id_main_cat, nombre, id_subcat FROM subcategoria")
        subcat_map = {(row[0], row[1]): row[2] for row in cursor.fetchall()}

        # 4. Productos
        print("Insertando productos...")
        product_query = """
            INSERT INTO producto (
                id_producto, descripcion, precio, rating, reviews_count,
                stock, url, image_url, id_marca, id_subcat
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                descripcion    = VALUES(descripcion),
                precio         = VALUES(precio),
                rating         = VALUES(rating),
                reviews_count  = VALUES(reviews_count),
                stock          = VALUES(stock)
        """

        products_data = []
        for _, row in df.iterrows():
            brand_id  = brand_map.get(str(row["brand_name"]).strip())
            main_id   = main_cat_map.get(str(row["main_category"]).strip())
            sub_name  = str(row["subcategory"]).strip()
            subcat_id = subcat_map.get((main_id, sub_name))

            try:
                precio = float(row["price_numeric"])
            except Exception:
                precio = 0.0
            try:
                rating = float(row["rating"])
            except Exception:
                rating = 0.0
            try:
                reviews = int(row["reviews_count"])
            except Exception:
                reviews = 0
            try:
                stock = int(row["stock"])
            except Exception:
                stock = 0

            products_data.append((
                str(row["id"]).strip(),
                str(row["product_description"]),
                precio,
                rating,
                reviews,
                stock,
                str(row["url"]),
                str(row["image_url"]),
                brand_id,
                subcat_id
            ))

        cursor.executemany(product_query, products_data)
        conn.commit()

        print(f"Carga completada. Productos procesados: {len(products_data)}")

    except Error as e:
        print(f"Error MySQL: {e}")
    finally:
        if "conn" in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexion cerrada.")


if __name__ == "__main__":
    populate_database()
