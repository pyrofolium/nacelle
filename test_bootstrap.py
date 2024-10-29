import unittest
import asyncio
from bootstrap import insert_into_table
import aiosqlite


class TestBootstrap(unittest.IsolatedAsyncioTestCase):

    async def test_insert_into_table(self):
        async with aiosqlite.connect(":memory:") as conn:
            await conn.execute(
                "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, description TEXT, price REAL)"
            )
            sample_data = [
                {
                    "id": 1,
                    "name": "Sample Product",
                    "description": "Sample Description",
                    "price": 9.99,
                }
            ]

            await insert_into_table(conn, "products", sample_data)

            # Verify insertion
            cursor = await conn.execute("SELECT * FROM products")
            rows = await cursor.fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1], "Sample Product")


if __name__ == "__main__":
    unittest.main()
