"""
Modulo de Configuracion del Backend
Carga variables de entorno y define parametros globales del sistema.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env de la raiz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Config:
    # Base de datos MySQL
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "ecommerce_db")
    DB_CHARSET = "utf8mb4"

    # Servidor Flask
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    DEBUG = FLASK_ENV == "development"

    # CORS
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5000")
    ALLOWED_ORIGINS = [
        FRONTEND_ORIGIN,
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "null"
    ]

    # Archivo CSV origen
    CSV_PATH = (
        BASE_DIR
        / "conjunto_datos"
        / "amazon_tech_products_ecommerceGKALI.csv"
    )
    SQLITE_FALLBACK_PATH = BASE_DIR / "database" / "ecommerce_local.db"
