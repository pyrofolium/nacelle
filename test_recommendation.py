import unittest
from unittest.mock import AsyncMock, patch
import aiosqlite

from bootstrap import bootstrap
from recommendations import (
    get_product_data,
    get_customer_data,
    generate_recommendation_for_customer,
)


class TestRecommendations(unittest.IsolatedAsyncioTestCase):

    async def test_get_product_data(self):
        async with aiosqlite.connect(":memory:") as conn:
            await bootstrap(conn)
            product_data = await get_product_data(conn)
            self.assertEqual(len(product_data), 5)
            self.assertEqual(product_data[0]["name"], "Ergonomic Chair")

    async def test_get_customer_data(self):
        async with aiosqlite.connect(":memory:") as conn:
            await bootstrap(conn)
            customer_data = await get_customer_data(1, conn)
            self.assertEqual(customer_data["first_name"], "John")
            self.assertEqual(
                customer_data["biography"],
                "John Doe is a software developer with over 10 years of experience in the industry. He enjoys working on open-source projects and contributing to the tech community.",
            )


if __name__ == "__main__":
    unittest.main()
