import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def configured_path(name, default):
    path = Path(os.getenv(name, str(default)))
    return str(path if path.is_absolute() else BASE_DIR / path)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "local-development-key-change-before-deploy")
    DATABASE_PATH = configured_path(
        "DATABASE_PATH", BASE_DIR / "database" / "lepetit.sqlite3"
    )
    DATASET_CSV_PATH = configured_path(
        "DATASET_CSV_PATH",
        BASE_DIR / "database" / "data" / "amazon_tech_products_ecommerceGKALI.csv",
    )
    DATABASE_SCHEMA_PATH = str(BASE_DIR / "database" / "schema.sql")
    DATABASE_SEED_PATH = str(BASE_DIR / "database" / "seed.sql")
    USD_TO_COP_RATE = os.getenv("USD_TO_COP_RATE", "4200")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    TEMPLATES_AUTO_RELOAD = True
    SSL_CERT_FILE = os.getenv("SSL_CERT_FILE", "")
    SSL_KEY_FILE = os.getenv("SSL_KEY_FILE", "")
