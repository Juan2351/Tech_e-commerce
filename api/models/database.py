"""
Capa de Acceso a Datos (DAL) - Motor de Base de Datos
Soporta conexion primaria a MySQL 8.0+ y contingencia local SQLite
poblada desde el CSV para garantizar disponibilidad continua.
"""

import os
import csv
import sqlite3
from decimal import Decimal
from pathlib import Path
import mysql.connector
from mysql.connector import Error as MySQLError
from api.config import Config

_engine = None  # "MySQL" o "SQLite"
_mysql_available = None


def test_mysql_connection():
    """Prueba si el servidor MySQL esta activo y accesible."""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset=Config.DB_CHARSET,
            connection_timeout=3
        )
        if conn.is_connected():
            conn.close()
            return True
        return False
    except Exception:
        return False


def get_engine():
    """Determina y retorna el motor de base de datos activo."""
    global _engine, _mysql_available
    if _engine is not None:
        return _engine

    if test_mysql_connection():
        _engine = "MySQL"
        _mysql_available = True
    else:
        _engine = "SQLite"
        _mysql_available = False
        init_sqlite_from_csv()

    return _engine


def get_mysql_connection():
    """Retorna una conexion activa a MySQL."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset=Config.DB_CHARSET
    )


def init_sqlite_from_csv():
    """Inicializa la base de datos SQLite con el mismo esquema y datos del CSV."""
    db_path = Config.SQLITE_FALLBACK_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS marca (
            id_marca INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS categoria_principal (
            id_main_cat INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS subcategoria (
            id_subcat INTEGER PRIMARY KEY AUTOINCREMENT,
            id_main_cat INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            FOREIGN KEY (id_main_cat) REFERENCES categoria_principal(id_main_cat),
            UNIQUE (id_main_cat, nombre)
        );

        CREATE TABLE IF NOT EXISTS producto (
            id_producto TEXT PRIMARY KEY,
            descripcion TEXT NOT NULL,
            precio REAL NOT NULL,
            rating REAL DEFAULT 0.00,
            reviews_count INTEGER DEFAULT 0,
            stock INTEGER NOT NULL DEFAULT 0,
            url TEXT,
            image_url TEXT,
            id_marca INTEGER,
            id_subcat INTEGER,
            FOREIGN KEY (id_marca) REFERENCES marca(id_marca),
            FOREIGN KEY (id_subcat) REFERENCES subcategoria(id_subcat)
        );
    """)

    # Verificar si ya tiene datos
    cur.execute("SELECT COUNT(*) FROM producto")
    count = cur.fetchone()[0]
    if count > 0:
        conn.close()
        return

    csv_path = Config.CSV_PATH
    if not csv_path.exists():
        conn.close()
        return

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    # Marcas
    marcas = sorted(set(r["brand_name"].strip() for r in reader if r.get("brand_name", "").strip()))
    for m in marcas:
        cur.execute("INSERT OR IGNORE INTO marca (nombre) VALUES (?)", (m,))

    # Categorias principales
    cats = sorted(set(r["main_category"].strip() for r in reader if r.get("main_category", "").strip()))
    for c in cats:
        cur.execute("INSERT OR IGNORE INTO categoria_principal (nombre) VALUES (?)", (c,))

    cur.execute("SELECT nombre, id_main_cat FROM categoria_principal")
    cat_map = dict(cur.fetchall())

    # Subcategorias
    subcats = set((r["subcategory"].strip(), r["main_category"].strip()) for r in reader if r.get("subcategory", "").strip() and r.get("main_category", "").strip())
    for s_name, c_name in subcats:
        c_id = cat_map.get(c_name)
        if c_id:
            cur.execute("INSERT OR IGNORE INTO subcategoria (id_main_cat, nombre) VALUES (?, ?)", (c_id, s_name))

    cur.execute("SELECT nombre, id_marca FROM marca")
    marca_map = dict(cur.fetchall())

    cur.execute("""
        SELECT s.nombre, c.nombre, s.id_subcat
        FROM subcategoria s
        JOIN categoria_principal c ON s.id_main_cat = c.id_main_cat
    """)
    subcat_map = {(s_name, c_name): s_id for s_name, c_name, s_id in cur.fetchall()}

    batch = []
    for r in reader:
        try:
            precio = float(str(r.get("price_numeric") or r.get("price", "0")).replace("$", "").replace(",", "").strip() or 0)
        except Exception:
            precio = 0.0
        try:
            rating = float(r.get("rating", "0").strip() or 0)
        except Exception:
            rating = 0.0
        try:
            reviews = int(r.get("reviews_count", "0").strip() or 0)
        except Exception:
            reviews = 0
        try:
            stock = int(r.get("stock", "0").strip() or 0)
        except Exception:
            stock = 0

        m_id = marca_map.get(r.get("brand_name", "").strip())
        s_id = subcat_map.get((r.get("subcategory", "").strip(), r.get("main_category", "").strip()))

        batch.append((
            r["id"].strip(),
            r["product_description"].strip(),
            precio,
            rating,
            reviews,
            stock,
            r.get("url", "").strip(),
            r.get("image_url", "").strip(),
            m_id,
            s_id
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO producto
        (id_producto, descripcion, precio, rating, reviews_count, stock, url, image_url, id_marca, id_subcat)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, batch)

    conn.commit()
    conn.close()


def query(sql, params=None, fetchone=False, commit=False):
    """
    Ejecuta una consulta SQL en el motor activo.
    Retorna diccionarios de filas.
    """
    engine = get_engine()
    params = params or []

    if engine == "MySQL":
        conn = get_mysql_connection()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params)
            if commit:
                conn.commit()
                return cur.rowcount
            return cur.fetchone() if fetchone else cur.fetchall()
        finally:
            conn.close()
    else:
        # SQLite: convertir placeholders %s a ?
        sqlite_sql = sql.replace("%s", "?")
        conn = sqlite3.connect(str(Config.SQLITE_FALLBACK_PATH))
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute(sqlite_sql, params)
            if commit:
                conn.commit()
                return cur.rowcount
            if fetchone:
                row = cur.fetchone()
                return dict(row) if row else None
            else:
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        finally:
            conn.close()
