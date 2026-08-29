import asyncpg
import asyncio
import os
from dotenv import load_dotenv
from logger import logger
load_dotenv()


async def init_db():
    # Берем строку подключения из .env (ту самую, что мы тестировали)
    db_url = os.getenv("DATABASE_URL")
    logger.info(f"🔍 Подключение к PostgreSQL: {db_url}")

    try:
        # 2. Подключение через asyncpg
        conn = await asyncpg.connect(db_url)
        logger.info("✅ Соединение установлено!")

        # 3. Выполнение запросов на создание таблиц
        # Подсказка: используй await conn.execute(ЗАПРОС) для каждого из трех
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS genres (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                release_year INTEGER CHECK (release_year >= 1800),
                rating NUMERIC(3, 1)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS movie_genres (
                movie_id INTEGER,
                genre_id INTEGER,
                PRIMARY KEY (movie_id, genre_id),
                FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
                FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
            );
        """)

        # 4. УБРАЛ цикл проверки файла! Вместо него:
        logger.info("✅ Таблицы успешно созданы в PostgreSQL!")

        # После создания всех таблиц
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        logger.info(f"📋 Созданные таблицы: {[row['tablename'] for row in tables]}")

        await conn.close()

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")



if __name__ == "__main__":
    asyncio.run(init_db())