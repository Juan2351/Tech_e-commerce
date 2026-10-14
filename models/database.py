from flask import current_app, g
import mysql.connector


class DatabaseConfigurationError(RuntimeError):
    pass


def get_db():
    if "db" not in g:
        config = current_app.config
        if not config["DB_USER"] or not config["DB_NAME"]:
            raise DatabaseConfigurationError(
                "Configura DB_USER y DB_NAME en el archivo .env."
            )
        g.db = mysql.connector.connect(
            host=config["DB_HOST"],
            port=config["DB_PORT"],
            user=config["DB_USER"],
            password=config["DB_PASSWORD"],
            database=config["DB_NAME"],
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            connection_timeout=5,
        )
    return g.db


def query_all(sql, params=()):
    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()


def query_one(sql, params=()):
    connection = get_db()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return cursor.fetchone()
    finally:
        cursor.close()


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None and connection.is_connected():
        connection.close()
