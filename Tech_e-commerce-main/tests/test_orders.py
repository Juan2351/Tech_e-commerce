import re
import unittest
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import create_app
from configs.settings import BASE_DIR
from models.database import get_db
from models.entities import Product


class CartOrderTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.product = Product(
            id_producto="LAP-ORDER-001",
            nombre="Laptop para pedido",
            descripcion="Producto de prueba",
            precio=Decimal("10.00"),
            rating=Decimal("4.5"),
            reviews_count=2,
            stock=5,
            url="",
            image_url="",
            id_marca=1,
            id_subcat=9,
            marca="Acer",
            subcategoria="General Laptops",
            categoria="Laptops & Notebooks",
            id_main_cat=4,
        )
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE_BACKEND": "sqlite",
            "DATABASE_PATH": str(
                Path(self.temporary_directory.name) / "orders.sqlite3"
            ),
            "DATASET_CSV_PATH": str(
                BASE_DIR / "database" / "data" / "amazon_tech_products_ecommerceGKALI.csv"
            ),
            "USD_TO_COP_RATE": "4200",
        })
        self.client = self.app.test_client()
        self.cart_summary = self.enterContext(patch(
            "controllers.shop_controller.cart_summary",
            return_value=(
                [{
                    "product": self.product,
                    "quantity": 2,
                    "subtotal": Decimal("20.00"),
                }],
                Decimal("20.00"),
            ),
        ))

    def test_checkout_creates_order_snapshot_and_clears_cart(self):
        with self.client.session_transaction() as current_session:
            current_session["cart"] = {"LAP-ORDER-001": 2}
            current_session["checkout_token"] = "single-use-checkout-token"

        response = self.client.post("/pedidos", data={
            "checkout_token": "single-use-checkout-token",
            "nombre": "Ana Pérez",
            "telefono": "+57 314 555 1234",
            "correo": "ana@example.com",
            "direccion": "Pereira",
        })

        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as current_session:
            order_number = current_session["last_order_number"]
            self.assertEqual(current_session["cart"], {})
            self.assertNotIn("checkout_token", current_session)
        self.assertRegex(order_number, re.compile(r"^LP-\d{8}-[A-F0-9]{8}$"))

        confirmation = self.client.get(response.headers["Location"])
        self.assertEqual(confirmation.status_code, 200)
        self.assertIn(order_number.encode(), confirmation.data)
        self.assertIn(b"Pendiente de confirmaci", confirmation.data)
        self.assertIn(b"Confirmar por WhatsApp", confirmation.data)
        self.assertIn(b"$ 84.000 COP", confirmation.data)

        with self.app.app_context():
            order = get_db().execute(
                "SELECT * FROM orders WHERE order_number = ?", (order_number,)
            ).fetchone()
            items = get_db().execute(
                "SELECT * FROM order_items WHERE order_id = ?", (order["id"],)
            ).fetchall()
        self.assertEqual(order["phone"], "+57 314 555 1234")
        self.assertEqual(order["status"], "pending_confirmation")
        self.assertEqual(order["total_cop"], 84000)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["quantity"], 2)

    def test_checkout_rejects_missing_or_invalid_form_token(self):
        response = self.client.post("/pedidos", data={
            "checkout_token": "forged-token",
            "nombre": "Ana Pérez",
            "telefono": "+57 314 555 1234",
        })
        self.assertEqual(response.status_code, 400)

    def test_cart_page_provides_single_use_checkout_token(self):
        with self.client.session_transaction() as current_session:
            current_session["cart"] = {"LAP-ORDER-001": 1}
        response = self.client.get("/carrito")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="checkout_token"', response.data)
        self.assertIn(b'name="nombre"', response.data)
        self.assertIn(b'name="telefono"', response.data)
        self.assertIn(b"Crear pedido y continuar", response.data)
        self.assertIn(b"no realiza ning\xc3\xban cobro", response.data)
        with self.client.session_transaction() as current_session:
            self.assertTrue(current_session["checkout_token"])

    def test_existing_database_gets_new_order_tables(self):
        with self.app.app_context():
            connection = get_db()
            connection.execute("DROP TABLE order_items")
            connection.execute("DROP TABLE orders")
            connection.commit()

        with self.app.app_context():
            connection = get_db()
            table_names = {
                row["name"]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
        self.assertIn("orders", table_names)
        self.assertIn("order_items", table_names)


if __name__ == "__main__":
    unittest.main()
