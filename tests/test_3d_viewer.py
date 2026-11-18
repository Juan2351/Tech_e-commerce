import unittest
from decimal import Decimal
from unittest.mock import patch

from app import create_app
from models.entities import Product


class Product3dViewerTests(unittest.TestCase):
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

    def test_home_includes_hero_3d_stage(self):
        with (
            patch(
                "controllers.shop_controller.catalog.fetch_categories",
                return_value=[],
            ),
            patch(
                "controllers.shop_controller.catalog.fetch_top_products",
                return_value=[self.product],
            ),
        ):
            response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'data-3d-hero', response.data)
        self.assertIn(b'data-product-category="General Laptops"', response.data)
        self.assertIn(b"/static/dist/app.js", response.data)
        self.assertIn(b"Ingresar", response.data)

    def test_product_3d_viewer_is_optional_and_category_aware(self):
        with patch(
            "controllers.shop_controller.catalog.fetch_product",
            return_value=self.product,
        ):
            response = self.client.get("/productos/LAP-TEST-001")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'data-product-3d-toggle', response.data)
        self.assertIn(b'aria-expanded="false"', response.data)
        self.assertIn(b'data-product-3d-panel hidden', response.data)
        self.assertIn(
            b'data-product-category="General Laptops Laptops &amp; Notebooks"',
            response.data,
        )
        self.assertIn(b'data-product-name="Laptop de prueba"', response.data)
        self.assertIn("Incluye Portátil 3D".encode("utf-8"), response.data)

    def test_shop_3d_filter_and_badges_identify_3d_products(self):
        non_3d_product = Product(
            id_producto="ACC-TEST-002",
            nombre="Cable organizador simple",
            descripcion="Accesorio genérico",
            precio=Decimal("9.99"),
            rating=Decimal("4.2"),
            reviews_count=4,
            stock=10,
            url="",
            image_url="",
            id_marca=1,
            id_subcat=99,
            marca="Genérico",
            subcategoria="Cables y Organizadores",
            categoria="Otros Accesorios",
            id_main_cat=9,
        )
        self.assertTrue(self.product.has_3d_model)
        self.assertEqual(self.product.model_3d_label, "Portátil 3D")
        self.assertFalse(non_3d_product.has_3d_model)

        with (
            patch(
                "controllers.shop_controller.catalog.fetch_categories",
                return_value=[],
            ),
            patch(
                "controllers.shop_controller.catalog.fetch_products",
                return_value=[self.product, non_3d_product],
            ),
        ):
            all_resp = self.client.get("/tienda")
            filtered_resp = self.client.get("/tienda?only_3d=1")

        self.assertEqual(all_resp.status_code, 200)
        self.assertIn(b"1 con Visor 3D Interactivo", all_resp.data)
        self.assertIn(b"Laptop de prueba", all_resp.data)
        self.assertIn(b"Cable organizador simple", all_resp.data)

        self.assertEqual(filtered_resp.status_code, 200)
        self.assertIn(b"Laptop de prueba", filtered_resp.data)
        self.assertNotIn(b"Cable organizador simple", filtered_resp.data)

    def test_home_team_section_includes_photos_and_bio_spaces(self):
        with (
            patch(
                "controllers.shop_controller.catalog.fetch_categories",
                return_value=[],
            ),
            patch(
                "controllers.shop_controller.catalog.fetch_top_products",
                return_value=[self.product],
            ),
        ):
            response = self.client.get("/")

        html = response.data.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn("about-team-grid", html)
        self.assertIn("team-member-bio", html)
        self.assertIn("/static/img/team/cristopher-arboleda.jpg", html)
        self.assertIn("/static/img/team/juan-jose-toro.jpg", html)
        self.assertIn("/static/img/team/kevin-ospina.jpg", html)
        self.assertIn("/static/img/team/juan-pablo-ruiz.jpg", html)


if __name__ == "__main__":
    unittest.main()
