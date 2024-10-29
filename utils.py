import asyncio

import aiofiles
import aiosqlite
from openai import AsyncOpenAI
import os

database_name = "store.db"


def remove_database():
    if os.path.isfile(database_name):
        os.remove(database_name)


def get_connection(name: str) -> aiosqlite.Connection:
    connection = aiosqlite.connect(name)
    return connection


def get_nacelle_connection() -> aiosqlite.Connection:
    return get_connection(database_name)


async def create_openai_client() -> AsyncOpenAI:
    try:
        file_paths = ["personal/organization", "personal/project", "personal/secret"]
        organization_id, project_id, secret_key = await asyncio.gather(
            *[read_file_async(path) for path in file_paths]
        )
        client = AsyncOpenAI(
            api_key=secret_key, organization=organization_id, project=project_id
        )
        return client
    except FileNotFoundError as e:
        print(
            """
        Credential file(s) nt found. Please follow the instructions below:

        Create a folder in this project called personal and place 3 files in it for openAI credentials.
        1. organization: contains the organization id
        2. project: contains the project id
        3. secret: contains the api key
        """
        )
        raise e


async def read_file_async(file_path: str) -> str:
    file = await aiofiles.open(file_path, "r")
    return await file.read()
