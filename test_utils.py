import unittest
import os
from utils import get_connection, read_file_async
import aiosqlite


class TestUtils(unittest.IsolatedAsyncioTestCase):

    async def test_get_connection(self):
        connection = await get_connection(
            ":memory:"
        )  # Use an in-memory database for testing
        self.assertIsInstance(connection, aiosqlite.Connection)
        await connection.close()

    async def test_read_file_async(self):
        # Create a temporary file for testing
        with open("test_file.txt", "w") as f:
            f.write("sample_content")

        # Test reading the file
        content = await read_file_async("test_file.txt")
        self.assertEqual(content, "sample_content")
        os.remove("test_file.txt")


if __name__ == "__main__":
    unittest.main()
