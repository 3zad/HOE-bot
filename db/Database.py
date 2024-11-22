import aiosqlite
from datetime import datetime

class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_name="economy.db"):
        self.db_name = db_name

    async def initialize(self):
        """Initialize the database by creating the necessary table."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                member_id INTEGER PRIMARY KEY,
                candy INTEGER DEFAULT 0,
                last_work_time TEXT DEFAULT NULL,
                stealing_attempts INTEGER DEFAULT 0,
                last_shield_time TEXT DEFAULT NULL,
                work_multiplier REAL DEFAULT 1.0
            )
            ''')
            print("here"*1000)
            await db.commit()

    async def add_or_update_user(self, member_id, candy=0, multiplier=1.0):
        """Add a new user or update an existing user's candy and multiplier."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            INSERT INTO user_data (member_id, candy, work_multiplier)
            VALUES (?, ?, ?)
            ON CONFLICT(member_id) DO UPDATE SET
                candy = candy + excluded.candy,
                work_multiplier = excluded.work_multiplier
            ''', (member_id, candy, multiplier))
            await db.commit()

    async def update_last_work_time(self, member_id):
        """Update the last work time for a user."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            UPDATE user_data
            SET last_work_time = ?
            WHERE member_id = ?
            ''', (datetime.now().isoformat(), member_id))
            await db.commit()

    async def get_user_data(self, member_id):
        """Retrieve data for a specific user."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            return row

    async def increment_stealing_attempts(self, member_id):
        """Increment the stealing attempts for a user."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            UPDATE user_data
            SET stealing_attempts = stealing_attempts + 1
            WHERE member_id = ?
            ''', (member_id,))
            await db.commit()

    async def update_last_shield_time(self, member_id):
        """Update the last shield time for a user."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            UPDATE user_data
            SET last_shield_time = ?
            WHERE member_id = ?
            ''', (datetime.now().isoformat(), member_id))
            await db.commit()
