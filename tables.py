from typing import List

marketing_campaigns_table = """
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    campaign_text TEXT,
    FOREIGN KEY (product_id) REFERENCES product(id)
)
"""

products_table = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    price REAL
)
"""

customer_feedback_table = """
CREATE TABLE IF NOT EXISTS customer_feedback (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,
    feedback TEXT,
    FOREIGN KEY (product_id) REFERENCES product(id)
)
"""

customers_table = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    biography TEXT
)
"""

# a group of tables that must be created in the order listed.
# if there is a sub group of tables in the list that means that subgroup can be created concurrently.
Tables = List[str | List[str]]
TABLES: Tables = [
    products_table,
    [marketing_campaigns_table, customer_feedback_table, customers_table],
]
