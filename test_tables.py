import unittest
import asyncio
import aiosqlite
from tables import TABLES


class TestTables(unittest.IsolatedAsyncioTestCase):

    async def test_tables_creation(self):
        async with aiosqlite.connect(":memory:") as conn:
            cursor = await conn.cursor()
            for table_script in TABLES:
                if isinstance(table_script, list):
                    await asyncio.gather(
                        *[cursor.execute(script) for script in table_script]
                    )
                else:
                    await cursor.execute(table_script)
            await conn.commit()

            # Check if tables were created successfully
            await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in await cursor.fetchall()]
            self.assertIn("products", tables)
            self.assertIn("marketing_campaigns", tables)
            self.assertIn("customer_feedback", tables)
            self.assertIn("customers", tables)


if __name__ == "__main__":
    unittest.main()
