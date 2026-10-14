import unittest
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import create_app
from configs.settings import BASE_DIR
from models.entities import Product
from models.database import DatabaseConfigurationError, get_db
from models.catalog import (
    fetch_categories as fetch_database_categories,
    fetch_product as fetch_database_product,
    fetch_products as fetch_database_products,
    fetch_products_by_ids as fetch_database_products_by_ids,
)


class LePetitApiTests(unittest.TestCase):
    def setUp(self):
        self.product = Product(
            id_producto="LAP-TEST-001",
            nombre="Laptop de prueba",
            descripcion="Descripción de prueba",
            precio=Decimal("79.99"),
            rating=Decimal("4.8"),
            reviews_count=12,
            stock=3,
            url="",
            image_url="",
            id_marca=1,
            id_subcat=1,
            marca="Acer",
            subcategoria="General Laptops",
            categoria="Laptops & Notebooks",
            id_main_cat=1,
        )
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
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
            return_value=[{"id_main_cat": 1, "nombre": "Laptops & Notebooks"}],
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
                [self.product] if "LAP-TEST-001" in product_ids else []
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
                "/api/v1/productos?category_id=1&q=Laptop&sort=price_asc"
            )
        self.assertEqual(response.status_code, 200)
        fetch_products.assert_called_once_with(1, None, "Laptop", "price_asc")

    def test_invalid_filter_returns_json_400(self):
        response = self.client.get("/api/v1/productos?category_id=0")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "invalid_query")

    def test_add_product_updates_session_and_returns_201(self):
        response = self.client.post(
            "/api/v1/carrito/productos",
            json={"product_id": "LAP-TEST-001", "quantity": 2},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["data"]["cart_count"], 2)
        with self.client.session_transaction() as current_session:
            self.assertEqual(current_session["cart"], {"LAP-TEST-001": 2})

    def test_non_integer_quantity_returns_400(self):
        response = self.client.post(
            "/api/v1/carrito/productos",
            json={"product_id": "LAP-TEST-001", "quantity": True},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "invalid_body")

    def test_quantity_above_stock_returns_409(self):
        response = self.client.post(
            "/api/v1/carrito/productos",
            json={"product_id": "LAP-TEST-001", "quantity": 4},
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
            current_session["cart"] = {"LAP-TEST-001": 1}

        update = self.client.patch(
            "/api/v1/carrito/productos/LAP-TEST-001", json={"quantity": 2}
        )
        self.assertEqual(update.status_code, 200)
        self.assertEqual(update.get_json()["data"]["quantity"], 2)

        delete = self.client.delete("/api/v1/carrito/productos/LAP-TEST-001")
        self.assertEqual(delete.status_code, 204)
        with self.client.session_transaction() as current_session:
            self.assertEqual(current_session["cart"], {})

    def test_update_of_product_not_already_in_cart_returns_404(self):
        response = self.client.patch(
            "/api/v1/carrito/productos/LAP-TEST-001", json={"quantity": 1}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"]["code"], "not_found")

    def test_html_catalog_renders_products_and_cop(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Laptop de prueba", response.data)
        self.assertIn(b"$ 335.958 COP", response.data)

    def test_exchange_rate_must_be_positive(self):
        with self.assertRaises(RuntimeError):
            create_app({"USD_TO_COP_RATE": "0"})

    def test_missing_catalog_returns_json_503(self):
        app = create_app({"TESTING": True, "SECRET_KEY": "test"})
        with patch(
            "controllers.api_controller.catalog.fetch_products",
            side_effect=DatabaseConfigurationError(
                "No se encontró el catálogo CSV requerido."
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
        self.assertEqual(response.get_json()["data"]["engine"], "SQLite")
        self.assertEqual(response.get_json()["data"]["database"], "lepetit.sqlite3")
        self.assertEqual(response.get_json()["data"]["usd_to_cop_rate"], "4200")

    def test_database_health_does_not_report_success_without_sql_result(self):
        with patch("controllers.api_controller.query_one", return_value=None):
            response = self.client.get("/api/v1/salud")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json()["error"]["code"], "database_unavailable"
        )

    def test_database_imports_all_technology_products_once(self):
        dataset = BASE_DIR / "database" / "data" / "amazon_tech_products_ecommerceGKALI.csv"
        with TemporaryDirectory() as temporary_directory:
            app = create_app({
                "DATABASE_PATH": str(Path(temporary_directory) / "catalog.sqlite3"),
                "DATASET_CSV_PATH": str(dataset),
            })
            with app.app_context():
                database = get_db()
                product_count = database.execute(
                    "SELECT COUNT(*) FROM producto"
                ).fetchone()[0]
                self.assertEqual(product_count, 3718)
                self.assertGreater(
                    database.execute(
                        "SELECT COUNT(*) FROM subcategoria WHERE nombre = 'Android Smartphones'"
                    ).fetchone()[0],
                    0,
                )
                self.assertGreater(
                    database.execute(
                        "SELECT COUNT(*) FROM subcategoria WHERE nombre = 'iPhones (Apple)'"
                    ).fetchone()[0],
                    0,
                )
            client = app.test_client()
            health = client.get("/api/v1/salud")
            self.assertEqual(health.status_code, 200)
            self.assertTrue(health.get_json()["data"]["connection"])

            with (
                patch(
                    "controllers.api_controller.catalog.fetch_products",
                    side_effect=fetch_database_products,
                ),
                patch(
                    "controllers.api_controller.catalog.fetch_product",
                    side_effect=fetch_database_product,
                ),
                patch(
                    "controllers.shop_controller.catalog.fetch_categories",
                    side_effect=fetch_database_categories,
                ),
                patch(
                    "controllers.shop_controller.catalog.fetch_products",
                    side_effect=fetch_database_products,
                ),
                patch(
                    "services.cart_service.fetch_product",
                    side_effect=fetch_database_product,
                ),
                patch(
                    "services.cart_service.fetch_products_by_ids",
                    side_effect=fetch_database_products_by_ids,
                ),
            ):
                products = client.get("/api/v1/productos?category_id=1")
                self.assertEqual(products.status_code, 200)
                self.assertEqual(len(products.get_json()["data"]), 568)
                first_product = products.get_json()["data"][0]
                self.assertEqual(first_product["categoria"], "Smartphones")

                detail = client.get(
                    f"/api/v1/productos/{first_product['id_producto']}"
                )
                self.assertEqual(detail.status_code, 200)
                self.assertEqual(
                    detail.get_json()["data"]["id_producto"],
                    first_product["id_producto"],
                )

                with app.app_context():
                    available_product = get_db().execute(
                        "SELECT id_producto FROM producto WHERE stock > 0 LIMIT 1"
                    ).fetchone()["id_producto"]
                added = client.post(
                    "/api/v1/carrito/productos",
                    json={"product_id": available_product, "quantity": 1},
                )
                self.assertEqual(added.status_code, 201)
                self.assertEqual(added.get_json()["data"]["cart_count"], 1)
                cart = client.get("/carrito")
                self.assertEqual(cart.status_code, 200)
                self.assertIn(b"Tu carrito", cart.data)
                self.assertIn(available_product.encode(), cart.data)

                home = client.get("/")
                self.assertEqual(home.status_code, 200)
                self.assertIn(b"Tecnolog", home.data)
                self.assertEqual(home.data.count(b'class="product-card"'), 24)
                next_page = client.get("/?category_id=1&page=2")
                self.assertEqual(next_page.status_code, 200)
                self.assertIn(b"de 24", next_page.data)
            with app.app_context():
                self.assertEqual(
                    get_db().execute("SELECT COUNT(*) FROM producto").fetchone()[0],
                    3718,
                )

    def test_database_requires_the_catalog_csv(self):
        with TemporaryDirectory() as temporary_directory:
            app = create_app({
                "DATABASE_PATH": str(Path(temporary_directory) / "catalog.sqlite3"),
                "DATASET_CSV_PATH": str(Path(temporary_directory) / "missing.csv"),
            })
            with app.app_context():
                with self.assertRaises(DatabaseConfigurationError):
                    get_db()


if __name__ == "__main__":
    unittest.main()
