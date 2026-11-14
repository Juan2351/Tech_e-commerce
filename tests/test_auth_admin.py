import unittest
from unittest.mock import patch

from app import create_app
from models.auth_model import AuthError, authenticate_user, register_user


class AuthAndAdminTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "USD_TO_COP_RATE": "4200",
            "DATABASE_BACKEND": "sqlite",
        })
        self.client = self.app.test_client()

    def test_login_page_renders_form(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Iniciar", response.data)
        self.assertIn(b"correo", response.data)
        self.assertIn(b'class="required-asterisk"', response.data)
        self.assertIn(b'data-password-toggle="password"', response.data)

    def test_register_page_renders_form(self):
        response = self.client.get("/registro")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Crear", response.data)
        self.assertIn(b"Registrarme", response.data)
        self.assertIn(b'class="required-asterisk"', response.data)
        self.assertIn(b'data-password-toggle="password"', response.data)
        self.assertIn(b'data-password-toggle="confirm_password"', response.data)
        self.assertIn(b"Beneficios de Cliente Registrado", response.data)
        self.assertIn(b"Cliente VIP", response.data)

    def test_home_page_renders_membership_and_vip_benefits(self):
        with (
            patch("controllers.shop_controller.catalog.fetch_categories", return_value=[]),
            patch("controllers.shop_controller.catalog.fetch_top_products", return_value=[]),
        ):
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Beneficios de Registrarte y Programa VIP", response.data)
            self.assertIn(b"Cliente Registrado", response.data)
            self.assertIn(b"Cliente VIP", response.data)
            self.assertIn(b"10% de descuento", response.data)

    def test_admin_dashboard_requires_login(self):
        response = self.client.get("/admin/dashboard", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_admin_dashboard_denies_client_role(self):
        with self.client.session_transaction() as sess:
            sess["user"] = {
                "id": "client-test",
                "nombre": "Cliente Normal",
                "email": "normal@correo.com",
                "role": "cliente",
            }
        response = self.client.get("/admin/dashboard", follow_redirects=True)
        self.assertIn(b"Acceso denegado", response.data)

    def test_admin_dashboard_allows_admin_role(self):
        with self.client.session_transaction() as sess:
            sess["user"] = {
                "id": "admin-test",
                "nombre": "Super Admin",
                "email": "admin@lepetit.com",
                "role": "admin",
            }
        with (
            patch(
                "controllers.admin_controller.catalog.fetch_dashboard_stats",
                return_value={
                    "total_products": 3718,
                    "total_categories": 10,
                    "total_clients": 5,
                    "total_stock": 25000,
                    "total_value_usd": 1250000.0,
                    "low_stock_count": 2,
                },
            ),
            patch(
                "controllers.admin_controller.catalog.fetch_top_products",
                return_value=[],
            ),
            patch(
                "controllers.admin_controller.get_all_clients",
                return_value=[],
            ),
        ):
            response = self.client.get("/admin/dashboard")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Panel de Control", response.data)
            self.assertIn(b"3718", response.data)

    def test_register_user_validation(self):
        with self.assertRaises(AuthError):
            register_user("A", "correo@valido.com", "123456")  # nombre muy corto

        with self.assertRaises(AuthError):
            register_user("Valente", "correo_invalido", "123456")  # correo inválido

        with self.assertRaises(AuthError):
            register_user("Valente", "valente@correo.com", "123")  # contraseña corta

        with self.assertRaises(AuthError):
            register_user("Valente", "valente@correo.com", "123456", role="superusuario")

    def test_sqlite_usuarios_authentication_and_roles(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from models.database import get_db

        with TemporaryDirectory() as temp_dir:
            app = create_app({
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "DATABASE_BACKEND": "sqlite",
                "DATABASE_PATH": str(Path(temp_dir) / "auth_test.sqlite3"),
            })
            with app.app_context():
                user = register_user(
                    nombre="Laura VIP",
                    email="laura@lepetit.com",
                    password="password123",
                    telefono="+57 300 111 2233",
                    direccion_entrega="Av Circunvalar, Pereira",
                    role="vip",
                )
                self.assertEqual(user["rol"], "vip")
                self.assertEqual(user["nombre_usuario"], "Laura VIP")
                self.assertEqual(user["direccion_entrega"], "Av Circunvalar, Pereira")

                auth_by_email = authenticate_user("laura@lepetit.com", "password123")
                self.assertIsNotNone(auth_by_email)
                self.assertEqual(auth_by_email["id"], user["id"])
                self.assertEqual(auth_by_email["rol"], "vip")

                auth_by_username = authenticate_user("Laura VIP", "password123")
                self.assertIsNotNone(auth_by_username)
                self.assertEqual(auth_by_username["id"], user["id"])

                self.assertIsNone(authenticate_user("laura@lepetit.com", "wrongpass"))

                db = get_db()
                with self.assertRaises(Exception):
                    db.execute(
                        """
                        INSERT INTO usuarios (nombre_usuario, email, password_hash, rol)
                        VALUES ('Invalido', 'inv@test.com', 'hash', 'invitado')
                        """
                    )

    def test_logout_clears_session(self):
        with self.client.session_transaction() as sess:
            sess["user"] = {"id": "1", "nombre": "Test", "email": "t@t.com", "role": "cliente"}
        response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertNotIn("user", sess)

    def test_admin_can_change_user_role_to_vip(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from models.auth_model import get_user_by_id

        with TemporaryDirectory() as temp_dir:
            app = create_app({
                "TESTING": True,
                "SECRET_KEY": "test-secret",
                "DATABASE_BACKEND": "sqlite",
                "DATABASE_PATH": str(Path(temp_dir) / "role_test.sqlite3"),
            })
            client = app.test_client()
            with app.app_context():
                user = register_user(
                    nombre="Mateo Cliente",
                    email="mateo@lepetit.com",
                    password="password123",
                    role="cliente",
                )
                user_id = user["id"]
                self.assertEqual(user["rol"], "cliente")

            with client.session_transaction() as sess:
                sess["user"] = {
                    "id": 999,
                    "nombre": "Admin",
                    "email": "admin@lepetit.com",
                    "role": "admin",
                    "rol": "admin",
                }

            resp = client.post(
                f"/admin/clientes/{user_id}/rol",
                data={"rol": "vip"},
                follow_redirects=True,
            )
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"VIP", resp.data)

            with app.app_context():
                updated = get_user_by_id(user_id)
                self.assertEqual(updated["rol"], "vip")

    def test_csrf_protection_blocks_forged_post_when_enabled(self):
        app = create_app({
            "TESTING": True,
            "CSRF_ENABLED": True,
            "SECRET_KEY": "test-secret",
            "DATABASE_BACKEND": "sqlite",
        })
        client = app.test_client()
        # Sin token CSRF debe devolver 400
        forged = client.post("/login", data={"email": "a@b.com", "password": "123456"})
        self.assertEqual(forged.status_code, 400)

        # Con un token CSRF inválido aunque exista en sesión debe devolver 400
        client.get("/login")
        invalid = client.post(
            "/login",
            data={"csrf_token": "wrong-token", "email": "a@b.com", "password": "123456"},
        )
        self.assertEqual(invalid.status_code, 400)


if __name__ == "__main__":
    unittest.main()
