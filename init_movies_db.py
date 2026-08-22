import aiosqlite
import asyncio
from pathlib import Path
from logger import logger

DB_PATH = (Path(__file__).parent / "movies.db").resolve()


async def init_db():
    logger.info(f"🔍 init_db создаёт таблицы в: {DB_PATH}")
    async with aiosqlite.connect(DB_PATH) as db:
        # 1. Таблица жанров
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """
        )

        # 2. Таблица фильмов
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                release_year INTEGER CHECK (release_year >= 1800),
                rating REAL CHECK (rating >= 0.0 AND rating <= 10.0)
            )
        """
        )

        # 3. Связующая таблица (Many-to-Many)
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS movie_genres (
                movie_id INTEGER,
                genre_id INTEGER,
                PRIMARY KEY (movie_id, genre_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
                FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
            )
        """
        )

        await db.commit()

        max_retries = 5
        for i in range(max_retries):
            if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
                logger.info(f"База создана и готова! ({i + 1} попытка)")
                return
            logger.info(f" Ожидание появления файла БД... ({i + 1}/{max_retries})")
            await asyncio.sleep(0.5)

        raise FileNotFoundError(f"База данных {DB_PATH} не была создана!")


if __name__ == "__main__":
    asyncio.run(init_db())
