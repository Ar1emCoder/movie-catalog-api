import aiosqlite

DATABASE_URL = "finance_tracker.db"

# async def get_db():
#     await aiosqlite.connect
#     row_factory = aiosqlite.Row # Чтобы получать строки как словари
#     return row_factory


async def create_user(username: str, email: str, age: int = None):
    db = await aiosqlite.connect("finance_tracker.db")
    cursor = await db.execute("INSERT INTO users (username) VALUES (?)", (username,))
    await db.commit()
    user_id = cursor.lastrowid  # Lastrowid - ID последней вставленной строки
    await db.close()
    return {"id": user_id, "username": username, "email": email, "age": age}


async def get_user_by_id(user_id: int):
    conn = await aiosqlite.connect("finance_tracker.db")
    cursor = await conn.execute(
        "SELECT id, username FROM users WHERE id = ?", (user_id,)
    )
    result = await cursor.fetchone()  # возвращает одну строку или None
    if result is None:
        return None
    else:
        return {"id": result[0], "username": result[1]}


async def get_all_users():
    conn = await aiosqlite.connect("finance_tracker.db")
    cursor = await conn.execute("SELECT id, username FROM users")
    users = await cursor.fetchall()
    await conn.close()
    result = []
    for row in users:
        result.append([{"id": row[0], "username": row[1]}])
    return result
