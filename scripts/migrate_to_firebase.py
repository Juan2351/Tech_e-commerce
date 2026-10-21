import csv
import json
import os
import sys
import time
import urllib.request
from decimal import Decimal
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from configs.settings import Config

FIREBASE_URL = Config.FIREBASE_DATABASE_URL
CSV_PATH = Path(Config.DATASET_CSV_PATH)

SEED_CATEGORIES = {
    1: 'Smartphones',
    2: 'Mini PCs & Desktops',
    3: 'Mice & Keyboards',
    4: 'Laptops & Notebooks',
    5: 'Audio & Headphones',
    6: 'Monitors & Displays',
    7: 'Tablets & E-Readers',
    8: 'Smartwatches & Wearables',
    9: 'Storage & Networking',
    10: 'Accessories & Hubs',
}

CAT_NAME_TO_ID = {name: cid for cid, name in SEED_CATEGORIES.items()}

SEED_SUBCATEGORIES = {
    (1, 'Android Smartphones'): 1,
    (1, 'iPhones (Apple)'): 2,
    (2, 'Desktop PCs & All-in-Ones'): 3,
    (2, 'Mini PCs'): 4,
    (3, 'Computer Mice'): 5,
    (3, 'Keyboards'): 6,
    (4, 'Business Laptops'): 7,
    (4, 'Gaming Laptops'): 8,
    (4, 'General Laptops'): 9,
    (5, 'Earbuds & Headphones'): 10,
    (6, 'Monitors'): 11,
    (7, 'Tablets & E-Ink'): 12,
    (8, 'Smartwatches'): 13,
    (9, 'SSD & Networking'): 14,
    (10, 'Power & Docks'): 15,
}


def send_firebase_payload(path: str, data: dict):
    url = f"{FIREBASE_URL}/{path.strip('/')}.json"
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


def run_migration():
    print(f"[*] Iniciando migración canónica a Firebase RTDB: {FIREBASE_URL}")

    if not CSV_PATH.is_file():
        print(f"[!] Error: No se encontró el archivo CSV en {CSV_PATH}")
        sys.exit(1)

    categories_dict = {
        str(cid): {
            "id_main_cat": cid,
            "nombre": name,
            "descripcion": f"Equipos y componentes seleccionados de {name}.",
            "imagen": ""
        }
        for cid, name in SEED_CATEGORIES.items()
    }

    subcategories_dict = {
        str(sid): {
            "id_subcat": sid,
            "id_main_cat": key[0],
            "nombre": key[1],
        }
        for key, sid in SEED_SUBCATEGORIES.items()
    }

    brands_map = {}
    brand_counter = 1
    products_map = {}

    with CSV_PATH.open(encoding="utf-8-sig", newline="") as src:
        reader = csv.DictReader(src)
        for row in reader:
            cat_name = (row.get("main_category") or "").strip()
            subcat_name = (row.get("subcategory") or "").strip()
            brand_name = (row.get("brand_name") or "").strip()
            p_id = (row.get("id") or "").strip()
            p_desc = (row.get("product_description") or "").strip()

            if not cat_name or not subcat_name or not p_id:
                continue

            main_cat_id = CAT_NAME_TO_ID.get(cat_name)
            if not main_cat_id:
                continue

            subcat_id = SEED_SUBCATEGORIES.get((main_cat_id, subcat_name))
            if not subcat_id:
                continue

            if brand_name and brand_name not in brands_map:
                brands_map[brand_name] = {
                    "id_marca": brand_counter,
                    "nombre": brand_name,
                }
                brand_counter += 1
            brand_id = brands_map.get(brand_name, {}).get("id_marca", 1)

            try:
                price = float(row.get("price_numeric") or "0")
                rating = float(row.get("rating") or "0")
                reviews_count = int(row.get("reviews_count") or "0")
                stock = int(row.get("stock") or "10")
            except ValueError:
                price = 0.0
                rating = 0.0
                reviews_count = 0
                stock = 10

            products_map[p_id] = {
                "id_producto": p_id,
                "nombre": p_desc,
                "descripcion": f"{p_desc}. Calidad garantizada por {brand_name}.",
                "precio": price,
                "rating": rating,
                "reviews_count": reviews_count,
                "stock": stock,
                "url": (row.get("url") or "").strip(),
                "image_url": (row.get("image_url") or "").strip(),
                "id_marca": brand_id,
                "id_subcat": subcat_id,
                "marca": brand_name,
                "subcategoria": subcat_name,
                "categoria": cat_name,
                "id_main_cat": main_cat_id,
            }

    print(f"[*] Categorías canónicas: {len(categories_dict)}")
    print(f"[*] Subcategorías canónicas: {len(subcategories_dict)}")
    print(f"[*] Marcas: {len(brands_map)}")
    print(f"[*] Productos totales: {len(products_map)}")

    # Contar productos de Smartphones (categoría 1)
    smartphones_count = sum(1 for p in products_map.values() if p["id_main_cat"] == 1)
    print(f"[*] Productos en categoría 1 (Smartphones): {smartphones_count}")

    print("[*] Subiendo categorías a Firebase /categories.json...")
    send_firebase_payload("categories", categories_dict)

    print("[*] Subiendo subcategorías a Firebase /subcategories.json...")
    send_firebase_payload("subcategories", subcategories_dict)

    brands_dict = {str(m["id_marca"]): m for m in brands_map.values()}
    print("[*] Subiendo marcas a Firebase /brands.json...")
    send_firebase_payload("brands", brands_dict)

    print(f"[*] Subiendo {len(products_map)} productos a Firebase /products.json...")
    send_firebase_payload("products", products_map)

    default_users = {
        "admin-01": {
            "id": "admin-01",
            "nombre": "Administrador LePetit",
            "email": "admin@lepetit.com",
            "password_hash": generate_password_hash("admin123"),
            "role": "admin",
            "telefono": "+57 300 123 4567",
            "ciudad": "Bogotá, Colombia",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "cliente-01": {
            "id": "cliente-01",
            "nombre": "Juan Pérez",
            "email": "cliente@lepetit.com",
            "password_hash": generate_password_hash("cliente123"),
            "role": "cliente",
            "telefono": "+57 311 987 6543",
            "ciudad": "Medellín, Colombia",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    }
    print("[*] Subiendo usuarios iniciales a Firebase /users.json...")
    send_firebase_payload("users", default_users)

    print("\n[OK] ¡Migración canónica completada exitosamente a Firebase!")


if __name__ == "__main__":
    run_migration()
