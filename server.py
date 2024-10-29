import asyncio
from contextlib import asynccontextmanager
from typing import Union, Callable, Awaitable, Any

import aiosqlite
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from bootstrap import bootstrap
from recommendations import get_product_data, generate_recommendations_from_customer_id
from utils import get_nacelle_connection, create_openai_client, remove_database


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/products")
async def products():
    connection = await get_nacelle_connection()
    return await get_product_data(connection)


@app.get("/customer/{customer_id}")
async def recommendations(customer_id: int):
    connection, client = await asyncio.gather(
        get_nacelle_connection(), create_openai_client()
    )
    return await generate_recommendations_from_customer_id(
        customer_id, connection, client
    )


@app.exception_handler(LookupError)
async def lookup_error_handler(request: Request, exception: LookupError):
    return JSONResponse(
        status_code=404,
        content={"message": str(exception)},
    )
