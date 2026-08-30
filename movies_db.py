import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
db_pool: asyncpg.Pool = None

async def init_db_pool():
    global db_pool
    database_url = os.getenv("DATABASE_URL")
    db_pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
    print("Пул подключений к PostgreSQL создан")


async def close_db_pool():
    global db_pool
    if db_pool:
        await db_pool.close()
        print("Пул подключений закрыт")


async def get_db():
    async with db_pool.acquire() as connection:
        yield connection


async def add_genre(db, name: str):
    row = await db.fetchrow("INSERT INTO genres(name) VALUES ($1) RETURNING id", name)
    return {"id": row["id"], "name": name}


async def get_all_genres(db, skip: int = 0, limit: int = 100):
    row = await db.fetch(
        "SELECT id, name FROM genres LIMIT $1 OFFSET $2",  # LIMIT - сколько максимум вернуть, OFFSET - сколько пропустить с начала
        limit, skip
    )
    return [dict(r) for r in row]


async def add_movie(db, title: str, release_year: int, rating: float):
    row = await db.fetchrow(
        "INSERT INTO movies (title, release_year, rating) VALUES ($1, $2, $3) RETURNING id",
        title, release_year, rating
    )
    return {
        "id": row["id"],
        "title": title,
        "release_year": release_year,
        "rating": rating,
    }


async def get_all_movies(db, skip: int = 0, limit: int = 100):
    row = await db.fetch(
        "SELECT id, title, release_year, rating FROM movies LIMIT $1 OFFSET $2",
        limit, skip
    )
    return [dict(r) for r in row]


# Связь таблиц: жанр - фильм
async def add_genre_to_movie(db, movie_id: int, genre_id: int):
    await db.execute(
        "INSERT INTO movie_genres (movie_id, genre_id) VALUES ($1, $2)",
        movie_id, genre_id
    )


async def delete_movie(db, movie_id: int):
    row = await db.fetchrow("DELETE FROM movies WHERE id = $1 RETURNING id", movie_id)
    return row is not None


async def get_movie_with_genres(db, movie_id: int):
    row = await db.fetch(
        """
            SELECT m.id, m.title, m.release_year, m.rating, g.name
            FROM movies m
            LEFT JOIN movie_genres mg ON m.id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.id
            WHERE m.id = $1
            """,
        movie_id
    )
    if not row:
        return None

    return {
        "id": row[0]["id"],
        "title": row[0]["title"],
        "release_year": row[0]["release_year"],
        "rating": row[0]["rating"],
        "genres": [r["name"] for r in row if r["name"] is not None]
    }


async def update_movie(db, movie_id: int, title: str, release_year: int, rating: float):
    row = await db.fetchrow(
        "UPDATE movies SET title = $1, release_year = $2, rating = $3 WHERE id = $4 RETURNING id",
        title, release_year, rating, movie_id
    )
    return row is not None


async def get_movies_by_genre(db, genre: str, skip: int, limit: int):
    row = await db.fetch(
        """
        SELECT DISTINCT m.id, m.title, m.release_year, m.rating
        FROM movies m
        JOIN movie_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        WHERE g.name = $1
        LIMIT $2 OFFSET $3
    """,
        genre, limit, skip
    )
    return [dict(r) for r in row]


async def count_all_movies(db):
    row = await db.fetchrow("SELECT COUNT(*) FROM movies")
    return row[0]


async def count_movies_by_genre(db, genre: str):
    row = await db.fetchrow(
        """
        SELECT COUNT(DISTINCT m.id)
        FROM movies m
        JOIN movie_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        WHERE g.name = $1
    """,
        genre
    )
    return row[0]
