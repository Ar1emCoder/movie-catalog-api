import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


async def test_connection():
    # Собираем строку подключения (используем чистый postgresql:// для asyncpg)
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "movies_db")

    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    print(f"Пытаемся подключиться к: {host}:{port}/{db}...")

    try:
        # Подключаемся к БД
        conn = await asyncpg.connect(db_url)
        print("✅ Успешное подключение к PostgreSQL!")

        # Делаем простой тестовый запрос
        version = await conn.fetchval('SELECT version()')
        print(f"📦 Версия базы данных:\n{version}\n")

        # Проверяем, есть ли уже таблицы (на всякий случай)
        tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        print(f"📋 Существующие таблицы в схеме 'public': {[row['tablename'] for row in tables]}")

        await conn.close()
        print("🔌 Соединение закрыто.")

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())