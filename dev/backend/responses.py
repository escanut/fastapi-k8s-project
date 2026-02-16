import json
import os
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel

# We are giving the application async capabilities, so we need to import asyncpg to interact with the PostgreSQL database asynchronously.
import asyncpg 

# We are using Pydantic to define our data models for request and response validation. 
# This helps ensure that the data we receive and send is in the correct format and meets our requirements.
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    created_at: datetime



# For getting the database URL
async def get_db_url()->str:
    try:
                    
        user = os.getenv("DB_USER", "admin")
        password = os.getenv("DB_PASSWORD", "password")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", 5432)
        dbname = os.getenv("DB_NAME", "products")

        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    except Exception as e:
        print(f"Error loading environment variables: {e}")
        raise


async def get_all_db_products() -> List[ProductResponse]:
    # To handle connection release properly
    async with pool.acquire() as connection:
        rows = await connection.fetch("SELECT * FROM products ORDER BY created_at DESC")
        result = []

        for row in rows:
            row_dict = dict(row) # Convert asyncpg Record to a regular dictionary
            product = ProductResponse(**row_dict) # Create a ProductResponse instance from the dictionary

            result.append(product)

        return result
    


async def get_product_by_id(product_id: int) -> Optional[ProductResponse]:
    async with pool.acquire() as connection:
        row = await connection.fetchrow("SELECT * FROM products WHERE id = $1", product_id)
        if row:
            row_dict = dict(row) # Convert asyncpg Record to a regular dictionary
            return ProductResponse(**row_dict) # Create a ProductResponse instance from the dictionary
        return None
    

async def create_product(product: ProductCreate) -> ProductResponse:
    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            "INSERT INTO products (name, description, price) VALUES ($1, $2, $3) RETURNING *",
            product.name,
            product.description,
            product.price
        )
        row_dict = dict(row) # Convert asyncpg Record to a regular dictionary
        return ProductResponse(**row_dict) # Create a ProductResponse instance from the dictionary
    
async def delete_product(product_id: int) -> bool:
    async with pool.acquire() as connection:
        result = await connection.execute("DELETE FROM products WHERE id = $1", product_id)
        return result == "DELETE 1" # asyncpg returns "DELETE 1" if one row was deleted
    

async def check_db_connection() -> bool:
    try:
        async with pool.acquire() as connection:
            await connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

#------------------------------------

# Pool initialization
pool: Optional[asyncpg.Pool] = None

# We want only 10 maximum connections to the database to avoid overwhelming it, and at least 1 connection to ensure we can always connect when needed.
async def init_db_pool():
    global pool
    if pool is None:
        db_url = await get_db_url()
        pool = await asyncpg.create_pool(dsn=db_url, min_size=1, max_size=10)


async def close_db_pool():
    global pool
    if pool is not None:
        await pool.close()
        pool = None