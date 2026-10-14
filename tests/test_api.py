import unittest
from decimal import Decimal
from unittest.mock import patch

from app import create_app
from models.entities import Product
from models.database import DatabaseConfigurationError, get_db


class LePetitApiTests(unittest.TestCase):
    def setUp(self):
        self.product = Product(
            id_producto="LP-001",
            nombre="Chaqueta de prueba",
            descripcion="Descripción de prueba",
            precio=Decimal("79.99"),
            rating=Decimal("4.8"),
            reviews_count=12,
            stock=3,
            url="",
            image_url="",
            id_marca=1,
            id_subcat=1,
            marca="LePetit",
            subcategoria="Ropa casual",
            categoria="Mujer",
            id_main_cat=1,
        )
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DB_USER": "unused-in-tests",
            "DB_NAME": "unused-in-tests",
            "USD_TO_COP_RATE": "4200",
        })
        self.client = self.app.test_client()
        self.api_fetch_products = self.enterContext(patch(
            "controllers.api_controller.catalog.fetch_products",
            return_value=[self.product],
        ))
        self.api_fetch_product = self.enterContext(patch(
            "controllers.api_controller.catalog.fetch_product",
            return_value=self.product,
        ))
        self.enterContext(patch(
            "controllers.shop_controller.catalog.fetch_categories",
            return_value=[{"id_main_cat": 1, "nombre": "Mujer"}],
        ))
        self.enterContext(patch(
            "controllers.shop_controller.catalog.fetch_products",
            return_value=[self.product],
        ))
        self.enterContext(patch(
            "services.cart_service.fetch_product",
            return_value=self.product,
        ))
        self.enterContext(patch(
            "services.cart_service.fetch_products_by_ids",
            side_effect=lambda product_ids: (
                [self.product] if "LP-001" in product_ids else []
            ),
        ))

    def test_product_list_returns_cop_price(self):
        response = self.client.get("/api/v1/productos")
        self.assertEqual(response.status_code, 200)
        product = response.get_json()["data"][0]
        self.assertEqual(product["precio"], 335958)
        self.assertEqual(product["moneda"], "COP")
        self.assertEqual(product["precio_base_usd"], "79.99")

    def test_product_list_passes_valid_filters_to_repository(self):
        with patch(
            "controllers.api_controller.catalog.fetch_products",
            return_value=[self.product],
        ) as fetch_products:
            response = self.client.get(
                "/api/v1/productos?category_id=1&q=Chaqueta&sort=price_asc"
            )
        self.assertEqual(response.status_code, 200)
        fetch_products.assert_called_once_with(1, None, "Chaqueta", "price_asc")

    def test_invalid_filter_returns_json_400(self):
        response = self.client.get("/api/v1/productos?category_id=0")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "invalid_query")

    def test_add_product_updates_session_and_returns_201(self):
        response = self.client.post(
            "/api/v1/carrito/productos",
            json={"product_id": "LP-001", "quantity": 2},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["data"]["cart_count"], 2)
        with self.client.session_transaction() as current_session:
            self.assertEqual(current_session["cart"], {"LP-001": 2})

    def test_non_integer_quantity_returns_400(self):
        response = self.client.post(
            "/api/v1/carrito/productos",
            json={"product_id": "LP-001", "quantity": True},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "invalid_body")

    def test_quantity_above_stock_returns_409(self):
        response = self.client.post(
            "/api/v1/carrito/productos",
            json={"product_id": "LP-001", "quantity": 4},
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.get_json()["error"]["code"], "insufficient_stock"
        )

    def test_missing_product_returns_404(self):
        self.api_fetch_product.return_value = None
        with patch("services.cart_service.fetch_product", return_value=None):
            response = self.client.post(
                "/api/v1/carrito/productos",
                json={"product_id": "MISSING", "quantity": 1},
            )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"]["code"], "not_found")

    def test_cart_update_and_delete(self):
        with self.client.session_transaction() as current_session:
            current_session["cart"] = {"LP-001": 1}

        update = self.client.patch(
            "/api/v1/carrito/productos/LP-001", json={"quantity": 2}
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.get_json()["data"]["quantity"], 2)

        delete = self.client.delete("/api/v1/carrito/productos/LP-001")
        self.assertEqual(delete.status_code, 204)
        with self.client.session_transaction() as current_session:
            self.assertEqual(current_session["cart"], {})

    def test_update_of_product_not_already_in_cart_returns_404(self):
        response = self.client.patch(
            "/api/v1/carrito/productos/LP-001", json={"quantity": 1}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"]["code"], "not_found")

    def test_html_catalog_renders_products_and_cop(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Chaqueta de prueba", response.data)
        self.assertIn(b"$ 335.958 COP", response.data)

    def test_exchange_rate_must_be_positive(self):
        with self.assertRaises(RuntimeError):
            create_app({"USD_TO_COP_RATE": "0"})

    def test_missing_database_configuration_returns_json_503(self):
        app = create_app({"TESTING": True, "SECRET_KEY": "test"})
        with patch(
            "controllers.api_controller.catalog.fetch_products",
            side_effect=DatabaseConfigurationError(
                "Configura DB_USER y DB_NAME en el archivo .env."
            ),
        ):
            response = app.test_client().get("/api/v1/productos")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json()["error"]["code"], "database_unavailable"
        )

    def test_database_health_endpoint_runs_sql_and_returns_status(self):
        with patch(
            "controllers.api_controller.query_one",
            return_value={"connection_ok": 1},
        ) as query:
            response = self.client.get("/api/v1/salud")
        self.assertEqual(response.status_code, 200)
        query.assert_called_once_with("SELECT 1 AS connection_ok")
        self.assertEqual(response.get_json()["data"]["engine"], "MySQL")
        self.assertEqual(response.get_json()["data"]["usd_to_cop_rate"], "4200")

    def test_database_health_does_not_report_success_without_sql_result(self):
        with patch("controllers.api_controller.query_one", return_value=None):
            response = self.client.get("/api/v1/salud")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json()["error"]["code"], "database_unavailable"
        )

    def test_database_requires_user_and_database_name(self):
        app = create_app({"DB_USER": "", "DB_NAME": ""})
        with app.app_context():
            with self.assertRaises(DatabaseConfigurationError):
                get_db()


if __name__ == "__main__":
    unittest.main()
