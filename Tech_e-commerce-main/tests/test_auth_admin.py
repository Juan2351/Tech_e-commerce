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

    def test_register_page_renders_form(self):
        response = self.client.get("/registro")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Crear", response.data)
        self.assertIn(b"Registrarme", response.data)

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

    def test_logout_clears_session(self):
        with self.client.session_transaction() as sess:
            sess["user"] = {"id": "1", "nombre": "Test", "email": "t@t.com", "role": "cliente"}
        response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertNotIn("user", sess)


if __name__ == "__main__":
    unittest.main()
