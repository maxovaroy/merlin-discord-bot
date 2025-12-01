#database.py
import aiosqlite

DB_PATH = "./leveling.db"  # your SQLite database file

async def get_user(user_id: int):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT xp, level, messages FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            await cursor.close()
            return row
    except Exception as e:
        print(f"❌ Error fetching user {user_id}: {e}")
        return None
