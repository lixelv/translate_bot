import aiosqlite
import asyncio


class AsyncDB:
    def __init__(self, db_path):
        self.db_path = db_path

    async def do(self, query, params=None):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.cursor() as cursor:
                if params:
                    await cursor.execute(query, params)
                else:
                    await cursor.execute(query)
                await db.commit()

    async def read(self, query, params=None, fetchone=False):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.cursor() as cursor:
                if params:
                    await cursor.execute(query, params)
                else:
                    await cursor.execute(query)

                if fetchone:
                    result = await cursor.fetchone()
                else:
                    result = await cursor.fetchall()

                return result


class TranslateDB(AsyncDB):
    def __init__(self, db_path):
        super().__init__(db_path)
        asyncio.run(self.create_db())

    async def create_db(self):
        await self.do(""" 
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                lang TEXT NOT NULL,
                name TEXT NOT NULL,
                registration_date TEXT NOT NULL
            );""")

        await self.do("""
            CREATE TABLE IF NOT EXISTS prime (
                id INTEGER PRIMARY KEY,
                link TEXT NOT NULL UNIQUE,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES user(id)
            );""")
        await self.do("""
            CREATE TABLE IF NOT EXISTS target (
                id INTEGER PRIMARY KEY,
                link TEXT NOT NULL UNIQUE,
                lang TEXT NOT NULL,
                prime_id INTEGER,
                user_id INTEGER,
                FOREIGN KEY (prime_id) REFERENCES prime(id)
                FOREIGN KEY (user_id) REFERENCES user(id)
            );""")

        await self.do("""
            CREATE TABLE IF NOT EXISTS message (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prime_id INTEGER,
                prime_message_id INTEGER,
                target_id INTEGER,
                target_message_id INTEGER,
                FOREIGN KEY (prime_id) REFERENCES prime(id),
                FOREIGN KEY (target_id) REFERENCES target(id)
            );""")

    # region user
    async def add_user(self, user_id, name, lang, registration_date):
        await self.do(
            "INSERT INTO user (id, name, lang, registration_date) VALUES (?, ?, ?, ?)",
            (user_id, name, lang, registration_date),
        )

    async def user_exists(self, user_id):
        return bool(
            await self.read(
                "SELECT * FROM user WHERE id = ?", (user_id,), fetchone=True
            )
        )

    async def get_lang(self, user_id):
        return (
            await self.read(
                "SELECT lang FROM user WHERE id = ?", (user_id,), fetchone=True
            )
        )[0]

    async def get_user_on_prime(self, prime_id):
        return await self.read(
            "SELECT user_id FROM prime WHERE id = ?", (prime_id,), fetchone=True
        )[0]

    async def change_lang(self, user_id, lang):
        await self.do("UPDATE user SET lang = ? WHERE id = ?", (lang, user_id))

    # endregion
    # region prime
    async def add_prime(self, chat_id, link, user_id):
        await self.do(
            "INSERT INTO prime (id, link, user_id) VALUES (?, ?, ?)",
            (chat_id, link, user_id),
        )

    async def get_primes(self, user_id):
        return await self.read(
            "SELECT link, id FROM prime WHERE user_id = ?", (user_id,)
        )

    async def del_prime(self, prime_id):
        await self.do("DELETE FROM prime WHERE id = ?", (prime_id,))
        for index in await db.read(
            "SELECT id FROM target WHERE prime_id = ?", (prime_id,)
        ):
            await db.del_target(index[0])

    async def in_prime(self, chat_id):
        return bool(await self.read("SELECT * FROM prime WHERE id = ?", (chat_id,)))

    # endregion
    # region target
    async def add_target(self, chat_id, link, lang, prime_id, user_id):
        await self.do(
            "INSERT INTO target (id, link, lang, prime_id, user_id) VALUES (?, ?, ?, ?, ?)",
            (chat_id, link, lang, prime_id, user_id),
        )

    async def get_targets(self, prime_id):
        return await self.read(
            "SELECT lang, id FROM target WHERE prime_id = ?", (prime_id,)
        )

    async def get_user_targets(self, user_id):
        return await self.read(
            "SELECT link, id FROM target WHERE user_id = ?", (user_id,)
        )

    async def change_target_lang(self, target_id, lang):
        await self.do("UPDATE target SET lang = ? WHERE id = ?", (lang, target_id))

    async def del_target(self, target_id):
        await self.do("DELETE FROM target WHERE id = ?", (target_id,))

    async def in_target(self, chat_id):
        return bool(await self.read("SELECT * FROM target WHERE id = ?", (chat_id,)))

    # endregion


db = TranslateDB("db.db")
