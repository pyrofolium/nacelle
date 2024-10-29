import asyncio
import json
import pprint

import aiosqlite
from typing import List, Dict, Optional, Any

from openai import AsyncOpenAI

from utils import create_openai_client, get_nacelle_connection

ProductData = List[Dict[str, str | float]]
CustomerData = Dict[str, str]
JSON = List["JSON"] | str | None | Dict[str, "JSON"] | float


async def get_product_data(db_connection: aiosqlite.Connection) -> ProductData:
    query = """
    SELECT 
        p.name,
        p.description,
        p.price,
        GROUP_CONCAT(f.feedback, '|<>|') AS feedbacks,
        m.campaign_text
    FROM products p
    LEFT JOIN customer_feedback f ON p.id = f.product_id
    LEFT JOIN marketing_campaigns m ON p.id = m.product_id
    GROUP BY p.id
    """
    cursor = await db_connection.cursor()
    await cursor.execute(query)
    result = await cursor.fetchall()
    product_data = []
    for row in result:
        context = {
            "name": row[0],
            "description": row[1],
            "price": row[2],
            "feedbacks": [i.strip() for i in row[3].split("|<>|")],
            "campaign_text": row[4],
        }
        product_data.append(context)

    return product_data


async def get_customer_data(
    customer_id: int, db_connection: aiosqlite.Connection
) -> CustomerData:
    cursor = await db_connection.cursor()
    query = """
       SELECT id, first_name, last_name, biography 
       FROM customers 
       WHERE id = ?
       """
    await cursor.execute(query, (customer_id,))
    result = await cursor.fetchone()
    if result is None:
        raise LookupError(f"Customer with id {customer_id} is not found")
    customer_data = {
        "id": result[0],
        "first_name": result[1],
        "last_name": result[2],
        "biography": result[3],
    }
    return customer_data


async def get_all_customer_data(
    db_connection: aiosqlite.Connection,
) -> List[CustomerData]:
    cursor = await db_connection.cursor()
    query = """
           SELECT id, first_name, last_name, biography 
           FROM customers  
           """
    await cursor.execute(query)
    result = await cursor.fetchall()
    customer_data = [
        {
            "id": entry[0],
            "first_name": entry[1],
            "last_name": entry[2],
            "biography": entry[3],
        }
        for entry in result
    ]
    return customer_data


async def generate_recommendations(
    product_data: ProductData, client: AsyncOpenAI, connection: aiosqlite.Connection
) -> JSON:
    serialized_product_data = json.dumps(product_data)
    serialized_customer_data = json.dumps(await get_all_customer_data(connection))

    completion = await client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": f"""
                Given this json profile data about all existing customers: {serialized_customer_data} 

                and using this json data about products: {serialized_product_data}

                generate well a written report of product recommendations for all customers in json format.
                
                The json format should ONLY be an object with one property: "content".
                
                content should contain an array of objects with properties: customer_id, first_name, last_name, 
                recommendations ( which contains the string titles of each recommended product ONLY) and reason (a string description as to why it was recommended).
                """,
            }
        ],
    )
    return json.loads(completion.choices[0].message.content)


async def generate_recommendations_from_customer_id(
    customer_id: int, connection: aiosqlite.Connection, client: AsyncOpenAI
) -> Optional[Dict[str, Any]]:
    customer_data, product_data = await get_customer_data(
        customer_id, connection
    ), await get_product_data(connection)
    return await generate_recommendation_for_customer(
        customer_data, product_data, client
    )


async def generate_recommendation_for_customer(
    customer_data: CustomerData, product_data: ProductData, client: AsyncOpenAI
) -> Optional[Dict[str, Any]]:
    serialized_product_data = json.dumps(product_data)
    serialized_customer_data = json.dumps(customer_data)

    completion = await client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": f"""
                Given this json profile data about a customer: {serialized_customer_data} 
                
                and using this json data about products: ": {serialized_product_data}
                
                generate a well written and personalized recommendation for the customer in json format.
                
                The json format should ONLY be an object of this format:
                
                customer_id: int
                first_name: str
                last_name: str
                recommendations: List[str]
                reason: str
                
                Of course the object in content should be related to the given customer data and product data. 
                """,
            }
        ],
    )
    return json.loads(completion.choices[0].message.content)


async def main():
    connection, client = await asyncio.gather(
        get_nacelle_connection(), create_openai_client()
    )
    product_data = await get_product_data(connection)
    recommendations = await generate_recommendations(product_data, client, connection)
    await connection.close()
    return recommendations


if __name__ == "__main__":
    pprint.pprint(asyncio.run(main()))
    print("done")
