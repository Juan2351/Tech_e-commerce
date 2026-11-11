import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from configs.settings import Config
from models.auth_model import create_admin_user


def main():
    print("=" * 60)
    print("CREADOR DE ADMINISTRADOR EN FIREBASE - LEPETIT")
    print(f"Base de Datos: {Config.FIREBASE_DATABASE_URL}")
    print("=" * 60)

    nombre = input("Nombre del Administrador [Administrador LePetit]: ").strip() or "Administrador LePetit"
    email = input("Correo Electrónico [admin@lepetit.com]: ").strip() or "admin@lepetit.com"
    password = input("Contraseña [admin123]: ").strip() or "admin123"
    telefono = input("Teléfono [+57 300 123 4567]: ").strip() or "+57 300 123 4567"
    ciudad = input("Ciudad [Bogotá, Colombia]: ").strip() or "Bogotá, Colombia"

    try:
        user = create_admin_user(
            nombre=nombre,
            email=email,
            password=password,
            telefono=telefono,
            ciudad=ciudad,
        )
        print("\n[OK] Administrador configurado exitosamente en Firebase Realtime Database:")
        print(f"      - ID: {user['id']}")
        print(f"      - Nombre: {user['nombre']}")
        print(f"      - Email: {user['email']}")
        print(f"      - Rol: {user['role']}")
        print("      - Contraseña: (encriptada de forma segura con PBKDF2-SHA256)")
    except Exception as err:
        print(f"\n[ERROR] No fue posible guardar el administrador en Firebase: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
