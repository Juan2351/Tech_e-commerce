import sqlite3
from pathlib import Path

from flask import current_app, g

from models.database_setup import initialize_database
from models.database_errors import DatabaseConfigurationError


def get_db():
    if "db" not in g:
        config = current_app.config
        database_path = Path(config["DATABASE_PATH"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            initialize_database(
                connection,
                config["DATABASE_SCHEMA_PATH"],
                config["DATABASE_SEED_PATH"],
                config["DATASET_CSV_PATH"],
            )
        except (sqlite3.Error, DatabaseConfigurationError):
            connection.close()
            raise
        g.db = connection
    return g.db


def query_all(sql, params=()):
    connection = get_db()
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()


def query_one(sql, params=()):
    connection = get_db()
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params)
        return cursor.fetchone()
    finally:
        cursor.close()


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()
