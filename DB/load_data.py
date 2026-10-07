import pandas as pd
import mysql.connector
from mysql.connector import Error

# Configuración de conexión (ajusta usuario y contraseña según tu entorno local)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # pon aquí tu contraseña de MySQL
    'database': 'ecommerce_db'
}

CSV_PATH = 'conjunto_datos/amazon_tech_products_ecommerceGKALI.csv'

def populate_database():
    try:
        print("Conectando a MySQL...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print(f"Leyendo CSV desde {CSV_PATH}...")
        df = pd.read_csv(CSV_PATH)

        # ----------------------------------------------------
        # 1. Insertar Marcas únicas
        # ----------------------------------------------------
        print("Insertando marcas...")
        brands = df['brand_name'].dropna().unique()
        brand_insert_query = "INSERT IGNORE INTO marca (nombre) VALUES (%s)"
        cursor.executemany(brand_insert_query, [(str(b).strip(),) for b in brands])
        conn.commit()

        # Mapear marcas a sus IDs generados
        cursor.execute("SELECT nombre, id_marca FROM marca")
        brand_map = {name: brand_id for name, brand_id in cursor.fetchall()}

        # ----------------------------------------------------
        # 2. Insertar Categorías Principales únicas
        # ----------------------------------------------------
        print("Insertando categorías principales...")
        main_categories = df['main_category'].dropna().unique()
        main_cat_query = "INSERT IGNORE INTO categoria_principal (nombre) VALUES (%s)"
        cursor.executemany(main_cat_query, [(str(c).strip(),) for c in main_categories])
        conn.commit()

        cursor.execute("SELECT nombre, id_main_cat FROM categoria_principal")
        main_cat_map = {name: cat_id for name, cat_id in cursor.fetchall()}

        # ----------------------------------------------------
        # 3. Insertar Subcategorías con su id_main_cat correspondiente
        # ----------------------------------------------------
        print("Insertando subcategorías...")
        subcats_df = df[['main_category', 'subcategory']].dropna().drop_duplicates()
        subcat_data = []
        for _, row in subcats_df.iterrows():
            main_id = main_cat_map.get(str(row['main_category']).strip())
            sub_name = str(row['subcategory']).strip()
            if main_id and sub_name:
                subcat_data.append((main_id, sub_name))

        subcat_query = "INSERT IGNORE INTO subcategoria (id_main_cat, nombre) VALUES (%s, %s)"
        cursor.executemany(subcat_query, subcat_data)
        conn.commit()

        cursor.execute("SELECT id_main_cat, nombre, id_subcat FROM subcategoria")
        subcat_map = {(row[0], row[1]): row[2] for row in cursor.fetchall()}

        # ----------------------------------------------------
        # 4. Insertar Productos
        # ----------------------------------------------------
        print("Insertando productos...")
        product_query = """
        INSERT INTO producto (
            id_producto, descripcion, precio, rating, reviews_count,
            stock, url, image_url, id_marca, id_subcat
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            descripcion = VALUES(descripcion),
            precio = VALUES(precio),
            rating = VALUES(rating),
            reviews_count = VALUES(reviews_count),
            stock = VALUES(stock);
        """

        products_data = []
        for _, row in df.iterrows():
            brand_id = brand_map.get(str(row['brand_name']).strip())
            main_id = main_cat_map.get(str(row['main_category']).strip())
            sub_name = str(row['subcategory']).strip()
            subcat_id = subcat_map.get((main_id, sub_name))

            products_data.append((
                str(row['id']).strip(),
                str(row['product_description']),
                float(row['price_numeric']),
                float(row['rating']),
                int(row['reviews_count']),
                int(row['stock']),
                str(row['url']),
                str(row['image_url']),
                brand_id,
                subcat_id
            ))

        cursor.executemany(product_query, products_data)
        conn.commit()

        print(f"¡Carga completada con éxito! Se procesaron {len(products_data)} productos.")

    except Error as e:
        print(f"Error al conectar o insertar en MySQL: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexión cerrada.")

if __name__ == '__main__':
    populate_database()
