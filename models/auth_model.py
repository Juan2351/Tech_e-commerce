import time
import uuid
from typing import Any, Dict, List, Optional
from werkzeug.security import check_password_hash, generate_password_hash

from models.firebase_db import FirebaseDB


class AuthError(Exception):
    """Excepción para errores de autenticación o validación de usuario."""
    pass


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Valida credenciales contra la base de datos de Firebase.
    
    Retorna el diccionario de usuario si es válido, de lo contrario None.
    """
    clean_email = email.strip().lower()
    user = FirebaseDB.get_user_by_email(clean_email)
    if not user:
        return None

    stored_hash = user.get("password_hash", "")
    if check_password_hash(stored_hash, password):
        return user
    return None


def register_user(
    nombre: str,
    email: str,
    password: str,
    telefono: str = "",
    ciudad: str = "",
    role: str = "cliente",
) -> Dict[str, Any]:
    """Registra un nuevo usuario en Firebase con contraseña encriptada.
    
    Por seguridad en producción, todo registro web se asigna estrictamente con rol 'cliente'.
    """
    nombre = nombre.strip()
    email = email.strip().lower()
    password = password.strip()

    if len(nombre) < 2:
        raise AuthError("El nombre completo debe tener al menos 2 caracteres.")
    if "@" not in email or "." not in email:
        raise AuthError("Ingresa una dirección de correo electrónico válida.")
    if len(password) < 6:
        raise AuthError("La contraseña debe tener al menos 6 caracteres.")

    # Verificar si el correo ya existe en Firebase
    existing = FirebaseDB.get_user_by_email(email)
    if existing:
        raise AuthError("Ya existe una cuenta registrada con este correo electrónico.")

    user_id = f"user-{uuid.uuid4().hex[:8]}"
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

    new_user = {
        "id": user_id,
        "nombre": nombre,
        "email": email,
        "password_hash": generate_password_hash(password),
        "role": "cliente",  # Siempre cliente desde el registro público
        "telefono": telefono.strip(),
        "ciudad": ciudad.strip(),
        "created_at": now_str,
    }

    FirebaseDB.save_user(new_user)
    return new_user


def create_admin_user(
    nombre: str,
    email: str,
    password: str,
    telefono: str = "",
    ciudad: str = "",
) -> Dict[str, Any]:
    """Crea o promueve un usuario con rol 'admin' en Firebase."""
    email = email.strip().lower()
    existing = FirebaseDB.get_user_by_email(email)
    user_id = existing["id"] if existing else f"admin-{uuid.uuid4().hex[:6]}"
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

    admin_user = {
        "id": user_id,
        "nombre": nombre.strip() or "Administrador",
        "email": email,
        "password_hash": generate_password_hash(password),
        "role": "admin",
        "telefono": telefono.strip(),
        "ciudad": ciudad.strip(),
        "created_at": existing.get("created_at", now_str) if existing else now_str,
    }

    FirebaseDB.save_user(admin_user)
    return admin_user


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    return FirebaseDB.get_user_by_id(user_id)


def get_all_users() -> List[Dict[str, Any]]:
    """Retorna todos los usuarios ordenados por fecha de creación descendente."""
    users = FirebaseDB.get_users()
    users.sort(key=lambda u: str(u.get("created_at", "")), reverse=True)
    return users


def get_all_clients() -> List[Dict[str, Any]]:
    """Retorna únicamente los usuarios con rol 'cliente'."""
    users = get_all_users()
    return [u for u in users if u.get("role") != "admin"]
