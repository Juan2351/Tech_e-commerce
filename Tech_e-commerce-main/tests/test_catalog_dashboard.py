import unittest
from unittest.mock import patch

from models import catalog


class CatalogDashboardTests(unittest.TestCase):
    def test_sqlite_dashboard_metrics_are_calculated_from_inventory(self):
        with (
            patch("models.catalog.is_firebase_active", return_value=False),
            patch(
                "models.catalog.query_one",
                side_effect=[
                    {
                        "total_products": 7,
                        "total_stock": 24,
                        "total_value_usd": 251.357,
                        "low_stock_count": 3,
                    },
                    {"total_categories": 4},
                ],
            ) as query_one,
            patch(
                "models.catalog.FirebaseDB.get_users",
                return_value=[
                    {"role": "cliente"},
                    {"role": "admin"},
                    {"role": "cliente"},
                ],
            ),
        ):
            stats = catalog.fetch_dashboard_stats()

        self.assertEqual(stats, {
            "total_products": 7,
            "total_categories": 4,
            "total_clients": 2,
            "total_stock": 24,
            "total_value_usd": 251.36,
            "low_stock_count": 3,
        })
        self.assertEqual(query_one.call_count, 2)


if __name__ == "__main__":
    unittest.main()
