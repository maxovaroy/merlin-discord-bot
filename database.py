import aiosqlite

DB_NAME = "merlin.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 0,
                messages INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT xp, level, messages FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row:
            return row
        return None

async def update_user(user_id, xp, level, messages):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users(user_id, xp, level, messages)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                xp = excluded.xp,
                level = excluded.level,
                messages = excluded.messages
        """, (user_id, xp, level, messages))

        await db.commit()
