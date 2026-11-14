import hashlib
from pathlib import Path
import sqlite3
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from models.database_setup import initialize_database


def pbkdf2_werkzeug_hash(password: str, salt: str = "lepetit2026salt") -> str:
    iterations = 600000
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return f"pbkdf2:sha256:{iterations}${salt}${dk}"


def main():
    db_path = BASE_DIR / "database" / "lepetit.sqlite3"
    schema_path = BASE_DIR / "database" / "schema.sql"
    seed_path = BASE_DIR / "database" / "seed.sql"
    csv_path = BASE_DIR / "database" / "data" / "amazon_tech_products_ecommerceGKALI.csv"

    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        initialize_database(connection, schema_path, seed_path, csv_path)
        default_users = [
            (
                "admin_lepetit",
                "admin@lepetit.com",
                pbkdf2_werkzeug_hash("admin123"),
                "admin",
                "+57 300 123 4567",
                "Bogotá, Colombia",
            ),
            (
                "juan_perez",
                "cliente@lepetit.com",
                pbkdf2_werkzeug_hash("cliente123"),
                "cliente",
                "+57 311 987 6543",
                "Medellín, Colombia",
            ),
            (
                "camila_vip",
                "vip@lepetit.com",
                pbkdf2_werkzeug_hash("vip123"),
                "vip",
                "+57 314 597 1304",
                "Galicia, Pereira, Risaralda",
            ),
        ]
        connection.executemany(
            """
            INSERT OR IGNORE INTO usuarios (
                nombre_usuario, email, password_hash, rol, telefono, direccion_entrega
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            default_users,
        )
        connection.commit()

        tables = [
            "marca",
            "categoria_principal",
            "subcategoria",
            "producto",
            "usuarios",
            "orders",
            "order_items",
        ]
        print(f"[OK] Base de datos inicializada en: {db_path}")
        for table in tables:
            count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  - Tabla {table}: {count} registros")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
