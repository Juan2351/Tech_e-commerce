import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app import create_app
from flask_jwt_extended import create_access_token


class JwtDashAndDocsTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "JWT_SECRET_KEY": "test-jwt-secret-with-at-least-32-bytes",
            "DATABASE_BACKEND": "sqlite",
        })
        self.client = self.app.test_client()

    def token_for(self, role):
        with self.app.app_context():
            return create_access_token(
                identity=f"{role}-test",
                additional_claims={"role": role},
            )

    def test_api_login_issues_short_lived_bearer_token(self):
        with patch(
            "controllers.api_controller.authenticate_user",
            return_value={
                "id": "admin-1",
                "email": "admin@example.com",
                "role": "admin",
            },
        ):
            response = self.client.post(
                "/api/v1/auth/login",
                json={"email": "admin@example.com", "password": "valid-password"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]
        self.assertEqual(data["token_type"], "Bearer")
        self.assertEqual(data["expires_in"], 900)
        self.assertTrue(data["access_token"])

    def test_api_login_rejects_invalid_credentials(self):
        with patch("controllers.api_controller.authenticate_user", return_value=None):
            response = self.client.post(
                "/api/v1/auth/login",
                json={"email": "user@example.com", "password": "incorrect"},
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json()["error"]["code"], "invalid_credentials"
        )

    def test_admin_api_requires_admin_jwt_role(self):
        anonymous = self.client.get("/api/v1/admin/dashboard")
        self.assertEqual(anonymous.status_code, 401)
        self.assertEqual(
            anonymous.get_json()["error"]["code"], "authentication_required"
        )

        customer = self.client.get(
            "/api/v1/admin/dashboard",
            headers={"Authorization": f"Bearer {self.token_for('cliente')}"},
        )
        self.assertEqual(customer.status_code, 403)

        with patch(
            "controllers.api_controller.catalog.fetch_dashboard_stats",
            return_value={
                "total_products": 5,
                "total_categories": 2,
                "total_clients": 3,
                "total_stock": 12,
                "total_value_usd": 100.0,
                "low_stock_count": 1,
            },
        ):
            administrator = self.client.get(
                "/api/v1/admin/dashboard",
                headers={"Authorization": f"Bearer {self.token_for('admin')}"},
            )

        self.assertEqual(administrator.status_code, 200)
        self.assertEqual(
            administrator.get_json()["data"]["total_products"], 5
        )

    def test_swagger_ui_and_openapi_spec_are_available(self):
        ui = self.client.get("/api/docs/")
        spec = self.client.get("/api/openapi.yaml")

        self.assertEqual(ui.status_code, 200)
        self.assertIn(b'id="swagger-ui"', ui.data)
        self.assertIn(b"LePetit API", ui.data)
        self.assertEqual(spec.status_code, 200)
        self.assertIn(b"BearerAuth", spec.data)
        self.assertIn(b"/admin/dashboard", spec.data)
        spec.close()

    def test_dash_page_and_callbacks_require_admin_session(self):
        anonymous = self.client.get("/admin/analytics/")
        self.assertEqual(anonymous.status_code, 302)
        self.assertIn("/login", anonymous.headers["Location"])
        anonymous_callback = self.client.get(
            "/admin/analytics/_dash-layout"
        )
        self.assertEqual(anonymous_callback.status_code, 401)

        with self.client.session_transaction() as current_session:
            current_session["user"] = {
                "id": "client-test",
                "nombre": "Cliente",
                "email": "client@example.com",
                "role": "cliente",
            }
        client_callback = self.client.get("/admin/analytics/_dash-layout")
        self.assertEqual(client_callback.status_code, 403)
        client_update = self.client.post(
            "/admin/analytics/_dash-update-component", json={}
        )
        self.assertEqual(client_update.status_code, 403)

        with self.client.session_transaction() as current_session:
            current_session["user"] = {
                "id": "admin-test",
                "nombre": "Administradora",
                "email": "admin@example.com",
                "role": "admin",
            }
        admin_page = self.client.get("/admin/analytics/")
        admin_layout = self.client.get("/admin/analytics/_dash-layout")
        self.assertEqual(admin_page.status_code, 200)
        self.assertEqual(admin_layout.status_code, 200)
        self.assertIn(b"admin-analytics-stock", admin_layout.data)

    def test_footer_shows_location_and_whatsapp_contact(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Galicia, Pereira, Risaralda", response.data)
        self.assertIn(b"wa.me/573145971304", response.data)
        self.assertIn(b"+57 314 5971304", response.data)
        self.assertIn(b'class="whatsapp-floating-link"', response.data)
        self.assertIn(b"Escribir a LePetit por WhatsApp", response.data)

    def test_home_contact_uses_current_location_and_attention_line(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Galicia, Pereira, Risaralda, Colombia", response.data)
        self.assertIn(b'tel:+573145971304', response.data)
        self.assertIn(b"+57 314 5971304", response.data)
        self.assertIn(b"wa.me/573145971304", response.data)
        self.assertNotIn(b"(300) 123-4567", response.data)
        self.assertNotIn(b"Carrera 43A # 1-50", response.data)

    def test_admin_dash_callback_returns_metrics_and_stock_chart(self):
        callback_key = next(iter(self.app.extensions["admin_dash"].callback_map))
        with self.client.session_transaction() as current_session:
            current_session["user"] = {
                "id": "admin-test",
                "nombre": "Administradora",
                "email": "admin@example.com",
                "role": "admin",
            }
        with (
            patch(
                "controllers.admin_dash.catalog.fetch_dashboard_stats",
                return_value={
                    "total_products": 5,
                    "total_categories": 2,
                    "total_clients": 3,
                    "total_stock": 12,
                    "total_value_usd": 100.0,
                    "low_stock_count": 1,
                },
            ),
            patch(
                "controllers.admin_dash.catalog.fetch_top_products",
                return_value=[
                    SimpleNamespace(nombre="Laptop de prueba", stock=4)
                ],
            ),
        ):
            response = self.client.post(
                "/admin/analytics/_dash-update-component",
                json={
                    "output": callback_key,
                    "outputs": [
                        {"id": "admin-analytics-metrics", "property": "children"},
                        {"id": "admin-analytics-stock", "property": "figure"},
                    ],
                    "inputs": [
                        {
                            "id": "admin-analytics-refresh",
                            "property": "n_intervals",
                            "value": 0,
                        }
                    ],
                    "state": [],
                    "changedPropIds": ["admin-analytics-refresh.n_intervals"],
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["response"]
        self.assertEqual(
            payload["admin-analytics-stock"]["figure"]["data"][0]["x"], [4]
        )
        self.assertEqual(
            payload["admin-analytics-metrics"]["children"][0]["props"]["children"][1]["props"]["children"],
            5,
        )


if __name__ == "__main__":
    unittest.main()
