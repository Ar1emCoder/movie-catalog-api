import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
db_pool: asyncpg.Pool = None


async def init_db_pool():
    global db_pool
    database_url = os.getenv("DATABASE_URL_FINANCE")
    db_pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
    print("Пул для Finance Tracker создан")


async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()


async def get_db():
    async with db_pool.acquire() as connection:
        yield connection


async def create_user(db: asyncpg.Connection, username: str, email: str, age: int = None):
    # Используем fetchrow, чтобы получить RETURNING id
    row = await db.fetchrow(
        "INSERT INTO users (username, email, age) VALUES ($1, $2, $3) RETURNING id",
        username, email, age
    )
    return {
        "id": row["id"],
        "username": username,
        "email": email,
        "age": age
    }


async def get_user_by_id(db: asyncpg.Connection, user_id: int):
    row = await db.fetchrow(
        "SELECT id, username FROM users WHERE id = $1", user_id)
    if row is None:
        return None
    else:
        return {"id": row["id"], "username": row["username"]}


async def get_all_users(db: asyncpg.Connection):
    rows = await db.fetch("SELECT id, username FROM users")
    return [dict(row) for row in rows]
