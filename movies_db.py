import aiosqlite
from pathlib import Path

DB_PATH = (Path(__file__).parent / "movies.db").resolve()


async def get_db():
    print(f"🔍 get_db подключается к: {DB_PATH}")
    db = await aiosqlite.connect(DB_PATH)
    try:
        yield db  # отдаем соединение эндпоинту
    finally:
        await db.close()  # закрываем, когда все готово


async def add_genre(db, name: str):
    cursor = await db.execute("INSERT INTO genres(name) VALUES (?) ", (name,))
    await db.commit()
    return {"id": cursor.lastrowid, "name": name}


async def get_all_genres(db, skip: int = 0, limit: int = 100):
    cursor = await db.execute(
        "SELECT id, name FROM genres LIMIT ? OFFSET ?",  # LIMIT - сколько максимум вернуть, OFFSET - сколько пропустить с начала
        (limit, skip),
    )
    genres = await cursor.fetchall()
    # Превращаем список кортежей в список словарей
    return [{"id": row[0], "name": row[1]} for row in genres]


async def add_movie(db, title: str, release_year: int, rating: float):
    cursor = await db.execute(
        "INSERT INTO movies (title, release_year, rating) VALUES (?, ?, ?)",
        (title, release_year, rating),
    )
    await db.commit()
    return {
        "id": cursor.lastrowid,
        "title": title,
        "release_year": release_year,
        "rating": rating,
    }


async def get_all_movies(db, skip: int = 0, limit: int = 100):
    cursor = await db.execute(
        "SELECT id, title, release_year, rating FROM movies LIMIT ? OFFSET ?",
        (limit, skip),
    )
    movies = await cursor.fetchall()
    return [
        {"id": row[0], "title": row[1], "release_year": row[2], "rating": row[3]}
        for row in movies
    ]


# Связь таблиц: жанр - фильм
async def add_genre_to_movie(db, movie_id: int, genre_id: int):
    await db.execute("PRAGMA foreign_keys = ON")

    cursor = await db.execute(
        "INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)",
        (movie_id, genre_id),
    )
    await db.commit()


async def delete_movie(db, movie_id: int):
    cursor = await db.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    await db.commit()
    # возвращаем True, если удалилась хотя бы одна запись
    return cursor.rowcount > 0


async def get_movie_with_genres(db, movie_id: int):
    cursor = await db.execute(
        """
            SELECT m.id, m.title, m.release_year, m.rating, g.name
            FROM movies m
            LEFT JOIN movie_genres mg ON m.id = mg.movie_id
            LEFT JOIN genres g ON mg.genre_id = g.id
            WHERE m.id = ?
            """,
        (movie_id,),
    )

    rows = await cursor.fetchall()
    if not rows:
        return None
    return {
        "id": rows[0][0],
        "title": rows[0][1],
        "release_year": rows[0][2],
        "rating": rows[0][3],
        "genres": [row[4] for row in rows if row[4] is not None],
    }


async def update_movie(db, movie_id: int, title: str, release_year: int, rating: float):
    cursor = await db.execute(
        "UPDATE movies SET title = ?, release_year = ?, rating = ? WHERE id = ?",
        (title, release_year, rating, movie_id),
    )
    await db.commit()
    return cursor.rowcount > 0


async def get_movies_by_genre(db, genre: str, skip: int, limit: int):
    cursor = await db.execute(
        """
        SELECT DISTINCT m.id, m.title, m.release_year, m.rating
        FROM movies m
        JOIN movie_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        WHERE g.name = ?
        LIMIT ? OFFSET ?
    """,
        (genre, limit, skip),
    )
    movies = await cursor.fetchall()
    return [
        {"id": row[0], "title": row[1], "release_year": row[2], "rating": row[3]}
        for row in movies
    ]


async def count_all_movies(db):
    cursor = await db.execute("SELECT COUNT(*) FROM movies")
    row = await cursor.fetchone()  # ✅ fetchone вернет (count,)
    return row[0]  # ✅ row[0] — это само число


async def count_movies_by_genre(db, genre: str):
    cursor = await db.execute(
        """
        SELECT COUNT(DISTINCT m.id)
        FROM movies m
        JOIN movie_genres mg ON m.id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.id
        WHERE g.name = ?
    """,
        (genre,),
    )
    row = await cursor.fetchone()
    return row[0]
