import csv
import os

CSV_PATH = os.path.join('conjunto_datos', 'amazon_tech_products_ecommerceGKALI.csv')
OUTPUT_SQL = os.path.join('DB', '02_seeds.sql')

def escape_sql(val):
    if val is None:
        return "NULL"
    s = str(val).replace("'", "''").strip()
    return f"'{s}'"

def main():
    if not os.path.exists(CSV_PATH):
        print(f"Error: No se encontró el archivo en {CSV_PATH}")
        return

    brands = set()
    main_cats = set()
    subcats = set() # (main_category, subcategory)
    products = []

    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            b_name = row['brand_name'].strip()
            m_cat = row['main_category'].strip()
            s_cat = row['subcategory'].strip()

            if b_name:
                brands.add(b_name)
            if m_cat:
                main_cats.add(m_cat)
            if m_cat and s_cat:
                subcats.add((m_cat, s_cat))

            products.append({
                'id': row['id'].strip(),
                'desc': row['product_description'].strip(),
                'price': float(row['price_numeric']),
                'rating': float(row['rating']),
                'reviews': int(row['reviews_count']),
                'stock': int(row['stock']),
                'url': row['url'].strip(),
                'image_url': row['image_url'].strip(),
                'brand_name': b_name,
                'main_cat': m_cat,
                'subcat': s_cat
            })

    # Mapeos de IDs en orden determinista
    brand_map = {name: i + 1 for i, name in enumerate(sorted(brands))}
    main_cat_map = {name: i + 1 for i, name in enumerate(sorted(main_cats))}
    
    subcat_map = {}
    for i, (m, s) in enumerate(sorted(subcats)):
        subcat_map[(m, s)] = i + 1

    print(f"Generando {OUTPUT_SQL}...")
    with open(OUTPUT_SQL, mode='w', encoding='utf-8') as out:
        out.write("-- Archivo de poblado de datos (Paso 7)\n")
        out.write("USE ecommerce_db;\n\n")
        out.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        # 1. Marcas
        out.write("-- 1. Insertar Marcas\n")
        out.write("INSERT INTO marca (id_marca, nombre) VALUES\n")
        brand_values = [f"({b_id}, {escape_sql(name)})" for name, b_id in brand_map.items()]
        out.write(",\n".join(brand_values) + ";\n\n")

        # 2. Categorías principales
        out.write("-- 2. Insertar Categorias Principales\n")
        out.write("INSERT INTO categoria_principal (id_main_cat, nombre) VALUES\n")
        main_cat_values = [f"({c_id}, {escape_sql(name)})" for name, c_id in main_cat_map.items()]
        out.write(",\n".join(main_cat_values) + ";\n\n")

        # 3. Subcategorías
        out.write("-- 3. Insertar Subcategorias\n")
        out.write("INSERT INTO subcategoria (id_subcat, id_main_cat, nombre) VALUES\n")
        subcat_values = [
            f"({s_id}, {main_cat_map[m]}, {escape_sql(s)})"
            for (m, s), s_id in subcat_map.items()
        ]
        out.write(",\n".join(subcat_values) + ";\n\n")

        # 4. Productos
        out.write("-- 4. Insertar Productos (3718 registros)\n")
        out.write("INSERT INTO producto (id_producto, descripcion, precio, rating, reviews_count, stock, url, image_url, id_marca, id_subcat) VALUES\n")
        prod_values = []
        for p in products:
            b_id = brand_map.get(p['brand_name'], 'NULL')
            s_id = subcat_map.get((p['main_cat'], p['subcat']), 'NULL')
            prod_values.append(
                f"({escape_sql(p['id'])}, {escape_sql(p['desc'])}, {p['price']}, {p['rating']}, {p['reviews']}, {p['stock']}, {escape_sql(p['url'])}, {escape_sql(p['image_url'])}, {b_id}, {s_id})"
            )
        out.write(",\n".join(prod_values) + ";\n\n")
        out.write("SET FOREIGN_KEY_CHECKS = 1;\n")

    print(f"¡Listo! Se generó el archivo {OUTPUT_SQL} con éxito.")

if __name__ == '__main__':
    main()
