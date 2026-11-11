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


if __name__ == "__main__":
    unittest.main()
