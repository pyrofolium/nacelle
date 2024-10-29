#!/usr/bin/env python3

import asyncio
import json

import aiofiles
import aiosqlite
from typing import Dict, Any, List
from tables import TABLES
from utils import get_nacelle_connection, remove_database


async def bootstrap(connection: aiosqlite.Connection) -> None:
    await drop_all_tables(connection)
    cursor = await connection.cursor()
    for table in TABLES:
        if isinstance(table, str):
            await cursor.execute(table)
        elif isinstance(table, list):
            [await cursor.execute(i) for i in table]
        else:
            raise ValueError("Invalid table type")
    await fill_tables_from_json(connection)
    await connection.commit()


async def insert_into_table(
    connection: aiosqlite.Connection, table_name: str, data: List[Dict[str, Any]]
) -> None:
    cursor = await connection.cursor()
    for item in data:
        column_names = ", ".join(item.keys())
        place_holders = ", ".join(["?"] * len(item))
        values = tuple(item.values())
        await cursor.execute(
            f"INSERT INTO {table_name} ({column_names}) VALUES ({place_holders});",
            values,
        )
        await connection.commit()


async def fill_tables_from_json(connection: aiosqlite.Connection) -> None:
    # fill in product data first.
    file = await aiofiles.open("data/products-json.json", "r")
    text = await file.read()
    data = json.loads(text)
    await insert_into_table(connection, "products", data)

    file_names = [
        "data/marketing-campaigns-json.json",
        "data/customer-feedback-json.json",
        "data/customer-json.json",
    ]
    table_names = ["marketing_campaigns", "customer_feedback", "customers"]
    # insert the rest of the data async.
    for file_name, table_name in zip(file_names, table_names):
        file = await aiofiles.open(file_name, "r")
        text = await file.read()
        data = json.loads(text)
        await insert_into_table(connection, table_name, data)
        await file.close()


async def drop_all_tables(connection: aiosqlite.Connection) -> None:
    cursor = await connection.cursor()
    await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = await cursor.fetchall()
    [await cursor.execute(f"DROP TABLE IF EXISTS {table[0]};") for table in tables]
    await connection.commit()


async def main() -> None:
    connection = await get_nacelle_connection()
    await bootstrap(connection)
    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
