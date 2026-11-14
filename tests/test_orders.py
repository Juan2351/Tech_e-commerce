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
        self.assertIsNone(order["user_id"])
        self.assertEqual(order["phone"], "+57 314 555 1234")
        self.assertEqual(order["status"], "pending_confirmation")
        self.assertEqual(order["total_cop"], 84000)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["quantity"], 2)

    def test_checkout_links_order_to_usuario_and_sets_null_on_delete(self):
        from models.auth_model import register_user
        with self.app.app_context():
            vip_user = register_user(
                nombre="Camila VIP",
                email="camila.vip@example.com",
                password="secretpassword",
                telefono="+57 310 000 1111",
                direccion_entrega="Calle 10 #20-30, Pereira",
                role="vip",
            )

        with self.client.session_transaction() as current_session:
            current_session["user"] = {
                "id": vip_user["id"],
                "nombre": vip_user["nombre_usuario"],
                "email": vip_user["email"],
                "role": vip_user["rol"],
            }
            current_session["cart"] = {"LAP-ORDER-001": 2}
            current_session["checkout_token"] = "vip-checkout-token"

        response = self.client.post("/pedidos", data={
            "checkout_token": "vip-checkout-token",
            "nombre": "Camila VIP",
            "telefono": "+57 310 000 1111",
            "correo": "camila.vip@example.com",
            "direccion": "Calle 10 #20-30, Pereira",
        })
        self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            db = get_db()
            order = db.execute(
                "SELECT * FROM orders WHERE checkout_token = ?",
                ("vip-checkout-token",),
            ).fetchone()
            self.assertEqual(order["user_id"], vip_user["id"])
            self.assertEqual(order["total_cop"], 75600)

            db.execute("DELETE FROM usuarios WHERE id = ?", (vip_user["id"],))
            db.commit()

            order_after_delete = db.execute(
                "SELECT * FROM orders WHERE id = ?", (order["id"],)
            ).fetchone()
            self.assertIsNone(order_after_delete["user_id"])

    def test_vip_cart_shows_preferential_discount(self):
        with self.client.session_transaction() as current_session:
            current_session["cart"] = {"LAP-ORDER-001": 2}
            current_session["user"] = {
                "id": 99,
                "nombre": "Cliente VIP",
                "email": "vip@example.com",
                "role": "vip",
                "rol": "vip",
            }
        response = self.client.get("/carrito")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Beneficio VIP (10% dcto.)", response.data)
        self.assertIn(b"$ 75.600 COP", response.data)

    def test_cart_page_prefills_checkout_fields_for_authenticated_user(self):
        from models.auth_model import register_user
        with self.app.app_context():
            user = register_user(
                nombre="Carlos Cliente",
                email="carlos@example.com",
                password="password123",
                telefono="+57 315 222 3344",
                direccion_entrega="Cra 7 # 15-20, Pereira",
                role="cliente",
            )

        with self.client.session_transaction() as current_session:
            current_session["cart"] = {"LAP-ORDER-001": 1}
            current_session["user"] = {
                "id": user["id"],
                "nombre": user["nombre_usuario"],
                "email": user["email"],
                "role": user["rol"],
            }

        response = self.client.get("/carrito")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'value="Carlos Cliente"', response.data)
        self.assertIn(b'value="+57 315 222 3344"', response.data)
        self.assertIn(b'value="carlos@example.com"', response.data)
        self.assertIn(b'value="Cra 7 # 15-20, Pereira"', response.data)

    def test_authenticated_user_can_view_only_own_orders_in_mis_pedidos(self):
        from models.auth_model import register_user
        with self.app.app_context():
            user1 = register_user(
                nombre="Usuario Uno",
                email="uno@example.com",
                password="password123",
            )
            user2 = register_user(
                nombre="Usuario Dos",
                email="dos@example.com",
                password="password123",
            )
            db = get_db()
            db.execute(
                """
                INSERT INTO orders (
                    user_id, order_number, checkout_token, status,
                    customer_name, phone, email, delivery_address, total_cop
                ) VALUES
                    (?, 'LP-20261114-AAAA1111', 'tok-1', 'confirmed', 'Usuario Uno', '+573001112233', 'uno@example.com', 'Pereira', 84000),
                    (?, 'LP-20261114-BBBB2222', 'tok-2', 'pending_confirmation', 'Usuario Dos', '+573004445566', 'dos@example.com', 'Bogotá', 42000)
                """,
                (user1["id"], user2["id"]),
            )
            db.commit()

        unauth_resp = self.client.get("/mis-pedidos", follow_redirects=False)
        self.assertEqual(unauth_resp.status_code, 302)
        self.assertIn("/login", unauth_resp.headers["Location"])

        with self.client.session_transaction() as current_session:
            current_session["user"] = {
                "id": user1["id"],
                "nombre": user1["nombre_usuario"],
                "email": user1["email"],
                "role": user1["rol"],
            }

        response = self.client.get("/mis-pedidos")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"LP-20261114-AAAA1111", response.data)
        self.assertIn(b"Confirmado", response.data)
        self.assertNotIn(b"LP-20261114-BBBB2222", response.data)

    def test_cart_is_isolated_between_different_authenticated_users(self):
        from models.auth_model import register_user
        with self.app.app_context():
            vip_user = register_user(
                nombre="VIP User",
                email="vip_cart@example.com",
                password="password123",
                role="vip",
            )
            normal_user = register_user(
                nombre="Normal User",
                email="normal_cart@example.com",
                password="password123",
                role="cliente",
            )

        with patch("services.cart_service.fetch_product", return_value=self.product):
            # 1. Inicia sesión como VIP y agrega un portátil (cantidad 2)
            self.client.post("/login", data={
                "email": "vip_cart@example.com",
                "password": "password123",
            })
            add_vip = self.client.post(
                "/api/v1/carrito/productos",
                json={"product_id": "LAP-ORDER-001", "quantity": 2},
            )
            self.assertEqual(add_vip.status_code, 201)

            # 2. Cierra sesión e inicia sesión como cliente normal
            self.client.get("/logout")
            self.client.post("/login", data={
                "email": "normal_cart@example.com",
                "password": "password123",
            })
            with self.client.session_transaction() as sess:
                self.assertEqual(sess.get("cart"), {})

            # 3. El cliente normal agrega 1 unidad y luego la elimina de su carrito
            self.client.post(
                "/api/v1/carrito/productos",
                json={"product_id": "LAP-ORDER-001", "quantity": 1},
            )
            delete_normal = self.client.delete("/api/v1/carrito/productos/LAP-ORDER-001")
            self.assertEqual(delete_normal.status_code, 204)
            with self.client.session_transaction() as sess:
                self.assertEqual(sess.get("cart"), {})

            # 4. Cierra sesión el cliente normal y vuelve a entrar el VIP: su carrito sigue intacto
            self.client.get("/logout")
            self.client.post("/login", data={
                "email": "vip_cart@example.com",
                "password": "password123",
            })
            with self.client.session_transaction() as sess:
                self.assertEqual(sess.get("cart"), {"LAP-ORDER-001": 2})

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

    def test_admin_orders_management_and_stock_deduction(self):
        from models import catalog

        with self.app.app_context():
            catalog.save_product({
                "id_producto": "LAP-ORDER-001",
                "nombre": 'Lenovo V15 Laptop 15.6"',
                "descripcion": "Laptop de prueba",
                "precio": 79.99,
                "stock": 5,
                "rating": 4.5,
                "reviews_count": 10,
                "marca": "Lenovo",
                "id_main_cat": 1,
                "id_subcat": 1,
            })

        with self.client.session_transaction() as sess:
            sess["cart"] = {"LAP-ORDER-001": 2}
            sess["checkout_token"] = "valid-order-token-admin"

        create_resp = self.client.post("/pedidos", data={
            "checkout_token": "valid-order-token-admin",
            "nombre": "Cliente Pedido Admin",
            "telefono": "+57 314 000 1111",
            "direccion": "Calle 50 #10-20, Pereira",
        })
        self.assertEqual(create_resp.status_code, 302)

        with self.app.app_context():
            order_row = get_db().execute(
                "SELECT id, status FROM orders ORDER BY id DESC LIMIT 1"
            ).fetchone()
            order_id = order_row["id"]
            self.assertEqual(order_row["status"], "pending_confirmation")

        # Iniciar sesión como administrador en la sesión
        with self.client.session_transaction() as sess:
            sess["user"] = {
                "id": 1,
                "nombre": "Admin Test",
                "email": "admin@lepetit.com",
                "role": "admin",
                "rol": "admin",
            }

        list_resp = self.client.get("/admin/pedidos")
        self.assertEqual(list_resp.status_code, 200)
        self.assertIn(b"Cliente Pedido Admin", list_resp.data)

        # 1. Confirmar el pedido -> debe descontar 2 unidades (de 5 a 3)
        confirm_resp = self.client.post(
            f"/admin/pedidos/{order_id}/estado",
            data={"status": "confirmed"},
            follow_redirects=True,
        )
        self.assertEqual(confirm_resp.status_code, 200)
        with self.app.app_context():
            prod_after_confirm = catalog.fetch_product("LAP-ORDER-001")
            self.assertEqual(prod_after_confirm.stock, 3)
            updated_order = get_db().execute(
                "SELECT status FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
            self.assertEqual(updated_order["status"], "confirmed")

        # 2. Cancelar el pedido confirmado -> debe revertir las 2 unidades (de 3 a 5)
        cancel_resp = self.client.post(
            f"/admin/pedidos/{order_id}/estado",
            data={"status": "cancelled"},
            follow_redirects=True,
        )
        self.assertEqual(cancel_resp.status_code, 200)
        with self.app.app_context():
            prod_after_cancel = catalog.fetch_product("LAP-ORDER-001")
            self.assertEqual(prod_after_cancel.stock, 5)
            cancelled_order = get_db().execute(
                "SELECT status FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
            self.assertEqual(cancelled_order["status"], "cancelled")

    def test_category_price_adjustment_and_coupons_by_category(self):
        from models import catalog

        with self.app.app_context():
            catalog.save_product({
                "id_producto": "LAP-CAT-100",
                "nombre": "Laptop Pro 14",
                "descripcion": "Equipo de prueba",
                "precio": 100.00,
                "stock": 10,
                "rating": 4.8,
                "reviews_count": 12,
                "marca": "Lenovo",
                "id_main_cat": 4,
                "id_subcat": 7,  # subcat 7 pertenece a id_main_cat = 4 (Laptops & Notebooks)
            })

        with self.client.session_transaction() as sess:
            sess["user"] = {
                "id": 1,
                "nombre": "Admin Test",
                "email": "admin@lepetit.com",
                "role": "admin",
                "rol": "admin",
            }

        # 1. Aplicar descuento masivo de -20% a la categoría 4 (100.00 -> 80.00)
        adj_resp = self.client.post(
            "/admin/categorias",
            data={"action": "adjust_prices", "id_main_cat": "4", "percent_change": "-20"},
            follow_redirects=True,
        )
        self.assertEqual(adj_resp.status_code, 200)
        with self.app.app_context():
            updated_prod = catalog.fetch_product("LAP-CAT-100")
            self.assertEqual(updated_prod.precio, Decimal("80.00"))

        # 2. Crear un cupón del 15% para la categoría 4 (LAPTOPS15)
        cup_resp = self.client.post(
            "/admin/categorias",
            data={
                "action": "coupon_save",
                "codigo": "PROMOLAP15",
                "porcentaje_descuento": "15",
                "id_main_cat": "4",
            },
            follow_redirects=True,
        )
        self.assertEqual(cup_resp.status_code, 200)
        self.assertIn(b"PROMOLAP15", cup_resp.data)

        # 3. Redimir el cupón en el carrito (self.product tiene id_main_cat=4)
        with self.client.session_transaction() as sess:
            sess["user"] = {
                "id": 2,
                "nombre": "Cliente Normal",
                "email": "cliente@lepetit.com",
                "role": "cliente",
                "rol": "cliente",
            }
            sess["cart"] = {"LAP-ORDER-001": 1}

        apply_resp = self.client.post(
            "/carrito/cupon",
            data={"codigo": "PROMOLAP15"},
            follow_redirects=True,
        )
        self.assertEqual(apply_resp.status_code, 200)
        self.assertIn(b"PROMOLAP15", apply_resp.data)
        self.assertIn(b"15% dcto.", apply_resp.data)


if __name__ == "__main__":
    unittest.main()
