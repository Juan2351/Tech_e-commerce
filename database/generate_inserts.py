"""
Script Generador de Seeds SQL
Genera el archivo database/02_seeds.sql a partir del CSV fuente.

Uso (ejecutar desde la raiz del proyecto):
    python database/generate_inserts.py

Salida: database/02_seeds.sql
"""

import csv
import os
from pathlib import Path

# Rutas relativas a la raiz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "conjunto_datos" / "amazon_tech_products_ecommerceGKALI.csv"
OUTPUT_SQL = Path(__file__).resolve().parent / "02_seeds.sql"


def escape_sql(val):
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''").strip()
    return f"'{s}'"


def main():
    if not CSV_PATH.exists():
        print(f"Error: No se encontro el archivo CSV en {CSV_PATH}")
        return

    brands = set()
    main_cats = set()
    subcats = set()
    products = []

    print(f"Leyendo CSV desde {CSV_PATH}...")
    with open(CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            b_name = row["brand_name"].strip()
            m_cat = row["main_category"].strip()
            s_cat = row["subcategory"].strip()

            if b_name:
                brands.add(b_name)
            if m_cat:
                main_cats.add(m_cat)
            if m_cat and s_cat:
                subcats.add((m_cat, s_cat))

            try:
                price = float(row["price_numeric"])
            except (ValueError, KeyError):
                price = 0.0
            try:
                rating = float(row["rating"])
            except (ValueError, KeyError):
                rating = 0.0
            try:
                reviews = int(row["reviews_count"])
            except (ValueError, KeyError):
                reviews = 0
            try:
                stock = int(row["stock"])
            except (ValueError, KeyError):
                stock = 0

            products.append({
                "id": row["id"].strip(),
                "desc": row["product_description"].strip(),
                "price": price,
                "rating": rating,
                "reviews": reviews,
                "stock": stock,
                "url": row["url"].strip(),
                "image_url": row["image_url"].strip(),
                "brand_name": b_name,
                "main_cat": m_cat,
                "subcat": s_cat
            })

    brand_map = {name: i + 1 for i, name in enumerate(sorted(brands))}
    main_cat_map = {name: i + 1 for i, name in enumerate(sorted(main_cats))}

    subcat_map = {}
    for i, (m, s) in enumerate(sorted(subcats)):
        subcat_map[(m, s)] = i + 1

    print(f"Generando {OUTPUT_SQL}...")
    with open(OUTPUT_SQL, mode="w", encoding="utf-8") as out:
        out.write("-- Archivo de poblado de datos generado automaticamente\n")
        out.write("-- Ejecutar DESPUES de database/schema.sql\n")
        out.write("USE ecommerce_db;\n\n")
        out.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        out.write("-- 1. Insertar Marcas\n")
        out.write("INSERT INTO marca (id_marca, nombre) VALUES\n")
        brand_values = [f"({b_id}, {escape_sql(name)})" for name, b_id in sorted(brand_map.items(), key=lambda x: x[1])]
        out.write(",\n".join(brand_values) + ";\n\n")

        out.write("-- 2. Insertar Categorias Principales\n")
        out.write("INSERT INTO categoria_principal (id_main_cat, nombre) VALUES\n")
        main_cat_values = [f"({c_id}, {escape_sql(name)})" for name, c_id in sorted(main_cat_map.items(), key=lambda x: x[1])]
        out.write(",\n".join(main_cat_values) + ";\n\n")

        out.write("-- 3. Insertar Subcategorias\n")
        out.write("INSERT INTO subcategoria (id_subcat, id_main_cat, nombre) VALUES\n")
        subcat_values = [
            f"({s_id}, {main_cat_map[m]}, {escape_sql(s)})"
            for (m, s), s_id in sorted(subcat_map.items(), key=lambda x: x[1])
        ]
        out.write(",\n".join(subcat_values) + ";\n\n")

        out.write("-- 4. Insertar Productos (3718 registros)\n")
        out.write("INSERT INTO producto (id_producto, descripcion, precio, rating, reviews_count, stock, url, image_url, id_marca, id_subcat) VALUES\n")
        prod_values = []
        for p in products:
            b_id = brand_map.get(p["brand_name"], "NULL")
            s_id = subcat_map.get((p["main_cat"], p["subcat"]), "NULL")
            prod_values.append(
                f"({escape_sql(p['id'])}, {escape_sql(p['desc'])}, {p['price']}, {p['rating']}, {p['reviews']}, {p['stock']}, {escape_sql(p['url'])}, {escape_sql(p['image_url'])}, {b_id}, {s_id})"
            )
        out.write(",\n".join(prod_values) + ";\n\n")
        out.write("SET FOREIGN_KEY_CHECKS = 1;\n")

    print(f"Listo. Archivo generado: {OUTPUT_SQL}")
    print(f"Total productos: {len(products)} | Marcas: {len(brands)} | Categorias: {len(main_cats)} | Subcategorias: {len(subcats)}")


if __name__ == "__main__":
    main()
