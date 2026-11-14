from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
import sqlite3
import time
import uuid
from typing import Any, Dict, List, Optional

from flask import current_app, has_app_context
from werkzeug.security import check_password_hash, generate_password_hash

from configs.settings import Config
from models.database import get_db
from models.database_setup import initialize_database
from models.firebase_db import FirebaseDB

VALID_ROLES = ("admin", "cliente", "vip")
VIP_DISCOUNT_RATE = Decimal("0.10")


class AuthError(Exception):
    """Excepción para errores de autenticación o validación de usuario."""
    pass


def _use_firebase() -> bool:
    if has_app_context():
        if current_app.config.get("TESTING"):
            return current_app.config.get("DATABASE_BACKEND") == "firebase"
        return current_app.config.get("DATABASE_BACKEND", "sqlite").lower() == "firebase"
    return Config.DATABASE_BACKEND.lower() == "firebase"


@contextmanager
def _sqlite_connection():
    if has_app_context():
        yield get_db()
        return

    database_path = Path(Config.DATABASE_PATH)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        initialize_database(
            connection,
            Config.DATABASE_SCHEMA_PATH,
            Config.DATABASE_SEED_PATH,
            Config.DATASET_CSV_PATH,
        )
        yield connection
    finally:
        connection.close()


def _row_to_user_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "nombre_usuario": row["nombre_usuario"],
        "nombre": row["nombre_usuario"],
        "email": row["email"],
        "password_hash": row["password_hash"],
        "rol": row["rol"],
        "role": row["rol"],
        "telefono": row["telefono"],
        "direccion_entrega": row["direccion_entrega"],
        "ciudad": row["direccion_entrega"],
        "created_at": row["created_at"],
    }


def get_vip_discount_rate(user: Optional[Dict[str, Any]]) -> Decimal:
    """Retorna el porcentaje de descuento preferencial si el usuario tiene rol 'vip'."""
    if not user:
        return Decimal("0.00")
    rol = (user.get("rol") or user.get("role") or "cliente").strip().lower()
    return VIP_DISCOUNT_RATE if rol == "vip" else Decimal("0.00")


def authenticate_user(email_or_username: str, password: str) -> Optional[Dict[str, Any]]:
    """Valida credenciales contra SQLite (tabla usuarios) o Firebase según configuración."""
    identifier = (email_or_username or "").strip()
    if not identifier or not password:
        return None

    if _use_firebase():
        user = FirebaseDB.get_user_by_email(identifier.lower())
        if not user:
            return None
        stored_hash = user.get("password_hash", "")
        if check_password_hash(stored_hash, password):
            rol = user.get("rol") or user.get("role", "cliente")
            user["rol"] = rol
            user["role"] = rol
            user.setdefault("nombre_usuario", user.get("nombre", ""))
            user.setdefault("direccion_entrega", user.get("ciudad", ""))
            return user
        return None

    with _sqlite_connection() as connection:
        row = connection.execute(
            """
            SELECT id, nombre_usuario, email, password_hash, rol,
                   telefono, direccion_entrega, created_at
            FROM usuarios
            WHERE lower(email) = lower(?) OR lower(nombre_usuario) = lower(?)
            """,
            (identifier, identifier),
        ).fetchone()

    if not row:
        return None

    if check_password_hash(row["password_hash"], password):
        return _row_to_user_dict(row)
    return None


def register_user(
    nombre: str,
    email: str,
    password: str,
    telefono: str = "",
    ciudad: str = "",
    role: str = "cliente",
    direccion_entrega: Optional[str] = None,
) -> Dict[str, Any]:
    """Registra un nuevo usuario con contraseña encriptada y rol validado."""
    nombre_limpio = (nombre or "").strip()
    email_limpio = (email or "").strip().lower()
    password_limpio = (password or "").strip()
    rol_final = (role or "cliente").strip().lower()
    direccion_final = (
        direccion_entrega.strip()
        if direccion_entrega is not None
        else (ciudad or "").strip()
    )

    if len(nombre_limpio) < 2:
        raise AuthError("El nombre completo debe tener al menos 2 caracteres.")
    if "@" not in email_limpio or "." not in email_limpio:
        raise AuthError("Ingresa una dirección de correo electrónico válida.")
    if len(password_limpio) < 6:
        raise AuthError("La contraseña debe tener al menos 6 caracteres.")
    if rol_final not in VALID_ROLES:
        raise AuthError(f"El rol debe ser uno de: {', '.join(VALID_ROLES)}.")

    if _use_firebase():
        existing = FirebaseDB.get_user_by_email(email_limpio)
        if existing:
            raise AuthError("Ya existe una cuenta registrada con este correo electrónico.")

        user_id = f"user-{uuid.uuid4().hex[:8]}"
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        new_user = {
            "id": user_id,
            "nombre_usuario": nombre_limpio,
            "nombre": nombre_limpio,
            "email": email_limpio,
            "password_hash": generate_password_hash(password_limpio),
            "rol": rol_final,
            "role": rol_final,
            "telefono": (telefono or "").strip(),
            "direccion_entrega": direccion_final,
            "ciudad": direccion_final,
            "created_at": now_str,
        }
        FirebaseDB.save_user(new_user)
        return new_user

    with _sqlite_connection() as connection:
        existing_email = connection.execute(
            "SELECT id FROM usuarios WHERE lower(email) = lower(?)",
            (email_limpio,),
        ).fetchone()
        if existing_email:
            raise AuthError("Ya existe una cuenta registrada con este correo electrónico.")

        existing_username = connection.execute(
            "SELECT id FROM usuarios WHERE lower(nombre_usuario) = lower(?)",
            (nombre_limpio,),
        ).fetchone()
        if existing_username:
            raise AuthError("Ya existe una cuenta registrada con este nombre de usuario.")

        cursor = connection.execute(
            """
            INSERT INTO usuarios (
                nombre_usuario, email, password_hash, rol, telefono, direccion_entrega
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                nombre_limpio,
                email_limpio,
                generate_password_hash(password_limpio),
                rol_final,
                (telefono or "").strip(),
                direccion_final,
            ),
        )
        connection.commit()
        row = connection.execute(
            """
            SELECT id, nombre_usuario, email, password_hash, rol,
                   telefono, direccion_entrega, created_at
            FROM usuarios
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        return _row_to_user_dict(row)


def create_admin_user(
    nombre: str,
    email: str,
    password: str,
    telefono: str = "",
    ciudad: str = "",
) -> Dict[str, Any]:
    """Crea o promueve un usuario con rol 'admin'."""
    email_limpio = (email or "").strip().lower()
    nombre_limpio = (nombre or "").strip() or "Administrador"
    telefono_limpio = (telefono or "").strip()
    direccion_limpia = (ciudad or "").strip()
    password_hash = generate_password_hash(password)

    if _use_firebase():
        existing = FirebaseDB.get_user_by_email(email_limpio)
        user_id = existing["id"] if existing else f"admin-{uuid.uuid4().hex[:6]}"
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        admin_user = {
            "id": user_id,
            "nombre_usuario": nombre_limpio,
            "nombre": nombre_limpio,
            "email": email_limpio,
            "password_hash": password_hash,
            "rol": "admin",
            "role": "admin",
            "telefono": telefono_limpio,
            "direccion_entrega": direccion_limpia,
            "ciudad": direccion_limpia,
            "created_at": existing.get("created_at", now_str) if existing else now_str,
        }
        FirebaseDB.save_user(admin_user)
        return admin_user

    with _sqlite_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM usuarios WHERE lower(email) = lower(?)",
            (email_limpio,),
        ).fetchone()
        if existing:
            connection.execute(
                """
                UPDATE usuarios
                SET nombre_usuario = ?, password_hash = ?, rol = 'admin',
                    telefono = ?, direccion_entrega = ?
                WHERE id = ?
                """,
                (
                    nombre_limpio,
                    password_hash,
                    telefono_limpio,
                    direccion_limpia,
                    existing["id"],
                ),
            )
            user_id = existing["id"]
        else:
            cursor = connection.execute(
                """
                INSERT INTO usuarios (
                    nombre_usuario, email, password_hash, rol, telefono, direccion_entrega
                ) VALUES (?, ?, ?, 'admin', ?, ?)
                """,
                (
                    nombre_limpio,
                    email_limpio,
                    password_hash,
                    telefono_limpio,
                    direccion_limpia,
                ),
            )
            user_id = cursor.lastrowid
        connection.commit()
        row = connection.execute(
            """
            SELECT id, nombre_usuario, email, password_hash, rol,
                   telefono, direccion_entrega, created_at
            FROM usuarios
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
        return _row_to_user_dict(row)


def get_user_by_id(user_id: Any) -> Optional[Dict[str, Any]]:
    if _use_firebase():
        return FirebaseDB.get_user_by_id(str(user_id))

    with _sqlite_connection() as connection:
        row = connection.execute(
            """
            SELECT id, nombre_usuario, email, password_hash, rol,
                   telefono, direccion_entrega, created_at
            FROM usuarios
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
    return _row_to_user_dict(row) if row else None


def get_all_users() -> List[Dict[str, Any]]:
    """Retorna todos los usuarios ordenados por fecha de creación descendente."""
    if _use_firebase():
        users = FirebaseDB.get_users()
        users.sort(key=lambda u: str(u.get("created_at", "")), reverse=True)
        return users

    with _sqlite_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, nombre_usuario, email, password_hash, rol,
                   telefono, direccion_entrega, created_at
            FROM usuarios
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()
    return [_row_to_user_dict(row) for row in rows]


def get_all_clients() -> List[Dict[str, Any]]:
    """Retorna los usuarios compradores (roles 'cliente' y 'vip')."""
    users = get_all_users()
    return [
        u for u in users
        if (u.get("rol") or u.get("role")) in ("cliente", "vip")
    ]
