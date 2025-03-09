import aiosqlite
from datetime import datetime
import random

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
                work_multiplier REAL DEFAULT 1.0,
                last_daily_time TEXT DEFAULT NULL,
                shield_hours INTEGER DEFAULT 0,
                lifetime_stealing_attempts INTEGER DEFAULT 0,
                gifts_claimed INTEGER DEFAULT 0,
                stolen_from INTEGER DEFAULT 0,
                work_count INTEGER DEFAULT 0,
                gambling_count INTEGER DEFAULT 0,
                worker_count INTEGER DEFAULT 0
            )
            ''')

            await db.execute('''
            CREATE TABLE IF NOT EXISTS lottery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candy_pot INTEGER DEFAULT 0
            )
            ''')

            await db.execute('''
            CREATE TABLE IF NOT EXISTS lottery_contributors (
                member_id INTEGER PRIMARY KEY,
                tickets INTEGER DEFAULT 0
            )
            ''')

            # Initialize the lottery pot if it is empty.
            cursor = await db.execute('SELECT COUNT(*) FROM lottery')
            row = await cursor.fetchone()
            if row[0] == 0:
                await db.execute("INSERT INTO lottery (candy_pot) VALUES (0)")

            await db.commit()


    # -------------- Admin -------------- #

    async def reset_balances(self):
        """Reset every user's balance to 1000 candy times their current multiplier."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                UPDATE user_data
                SET candy = 1000 * work_multiplier
            ''')
            await db.commit()


    # -------------- User -------------- #

    async def add_or_update_user(self, member_id, candy=0, multiplier=0, gifts=0, work_count=0, gambling_count=0, worker_count=0):
        """Add a new user or update an existing user's candy and multiplier."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT candy FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()

            if row is None:
                initial_candy = 1000 + candy
                await db.execute('''
                INSERT INTO user_data (member_id, candy, gifts_claimed, work_count, gambling_count, worker_count)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (member_id, initial_candy, gifts, work_count, gambling_count, worker_count))
            else:
                await db.execute('''
                UPDATE user_data
                SET candy = candy + ?, work_multiplier = work_multiplier + ?, gifts_claimed = gifts_claimed + ?, work_count = work_count + ?, gambling_count = gambling_count + ?, worker_count = worker_count + ?
                WHERE member_id = ?
                ''', (candy, multiplier, gifts, work_count, gambling_count, worker_count, member_id))
                
            await db.commit()

    async def ensure_column_exists(self, db, table_name, column_name, column_definition):
        """Ensures a column exists in the specified table. If not, adds it."""
        cursor = await db.execute(f"PRAGMA table_info({table_name})")
        columns = await cursor.fetchall()
        if column_name not in [col[1] for col in columns]:  # col[1] is the column name in PRAGMA results
            await db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
            await db.commit()

    async def add_or_update_user(self, member_id, candy=0, multiplier=0, gifts=0, work_count=0, gambling_count=0, worker_count=0):
        """Add a new user or update an existing user's candy and multiplier."""
        async with aiosqlite.connect(self.db_name) as db:
            # Ensure all required columns exist
            await self.ensure_column_exists(db, "user_data", "gifts_claimed", "INTEGER DEFAULT 0")
            await self.ensure_column_exists(db, "user_data", "work_count", "INTEGER DEFAULT 0")
            await self.ensure_column_exists(db, "user_data", "gambling_count", "INTEGER DEFAULT 0")
            await self.ensure_column_exists(db, "user_data", "worker_count", "INTEGER DEFAULT 0")
            await self.ensure_column_exists(db, "user_data", "work_multiplier", "REAL DEFAULT 1.0")

            # Check if the user already exists
            cursor = await db.execute('SELECT candy FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()

            if row is None:
                # Insert a new user
                initial_candy = 1000 + candy
                await db.execute('''
                INSERT INTO user_data (member_id, candy, gifts_claimed, work_count, gambling_count, worker_count)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (member_id, initial_candy, gifts, work_count, gambling_count, worker_count))
            else:
                # Update existing user
                await db.execute('''
                UPDATE user_data
                SET candy = candy + ?, work_multiplier = work_multiplier + ?, 
                    gifts_claimed = gifts_claimed + ?, work_count = work_count + ?, 
                    gambling_count = gambling_count + ?, worker_count = worker_count + ?
                WHERE member_id = ?
                ''', (candy, multiplier, gifts, work_count, gambling_count, worker_count, member_id))

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

    async def update_last_daily_time(self, member_id):
        """Update the last daily time for a user if it's been 20 hours or more."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            UPDATE user_data
            SET last_daily_time = ?
            WHERE member_id = ?
            ''', (datetime.now().isoformat(), member_id))
            await db.commit()

    async def get_user_data(self, member_id):
        """Retrieve data for a specific user."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            return row
        
    async def get_user_balance(self, member_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            try:
                return int(row[1])
            except TypeError:
                return 0
            
    async def get_user_stealing(self, member_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            try:
                return int(row[3])
            except TypeError:
                return 0
            
    async def get_user_multiplier(self, member_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            try:
                return int(row[5])
            except TypeError:
                return 1
            
    async def get_user_gifts(self, member_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            try:
                return int(row[9])
            except TypeError:
                return 0
            
    async def get_user_shield_date(self, member_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            try:
                return (row[4], row[7])
            except TypeError:
                return None
            
    async def get_user_stolen_from(self, member_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            try:
                return int(row[10])
            except TypeError:
                return 0
            
    async def get_user_workers(self, member_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM user_data WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            try:
                return int(row[13])
            except TypeError:
                return 0

    async def get_users_with_workers(self):
        """Retrieve all users with a worker count above 0."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
            SELECT member_id, worker_count 
            FROM user_data 
            WHERE worker_count > 0
            ''')
            users = await cursor.fetchall()
            return users

    async def get_user_tickets(self, member_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM lottery_contributors WHERE member_id = ?', (member_id,))
            row = await cursor.fetchone()
            try:
                return int(row[1])
            except TypeError:
                return 0

    async def increment_stealing_attempts(self, member_id):
        """Increment the stealing attempts for a user."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            UPDATE user_data
            SET stealing_attempts = stealing_attempts + 1, lifetime_stealing_attempts = lifetime_stealing_attempts + 1
            WHERE member_id = ?
            ''', (member_id,))
            await db.commit()

    async def increment_stolen_from(self, member_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            UPDATE user_data
            SET stolen_from = stolen_from + 1
            WHERE member_id = ?
            ''', (member_id,))
            await db.commit()

    async def clear_stealing_attempts(self, member_id):
        """Clear the stealing attempts for a user."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            UPDATE user_data
            SET stealing_attempts = 0
            WHERE member_id = ?
            ''', (member_id,))
            await db.commit()

    async def update_last_shield_time(self, member_id, hours):
        """Update the last shield time for a user."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
            UPDATE user_data
            SET last_shield_time = ?, shield_hours = ?
            WHERE member_id = ?
            ''', (datetime.now().isoformat(), hours, member_id))
            await db.commit()

    # -------------- Lottery -------------- #

    async def add_to_lottery(self, member_id, tickets):
        """Add user's contribution to the lottery."""
        candy = tickets * 25
        async with aiosqlite.connect(self.db_name) as db:
            # Update lottery pot
            await db.execute('''
            UPDATE lottery SET candy_pot = candy_pot + ?
            ''', (candy,))

            await db.execute('''
            INSERT INTO lottery_contributors (member_id, tickets)
            VALUES (?, ?)
            ON CONFLICT(member_id) DO UPDATE SET
                tickets = tickets + excluded.tickets
            ''', (member_id, tickets))

            # Deduct candy from user
            await db.execute('''
            UPDATE user_data SET candy = candy - ? WHERE member_id = ?
            ''', (candy, member_id))

            await db.commit()

    async def get_lottery_pot(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT candy_pot FROM lottery')
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def get_lottery_contributors(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM lottery_contributors')
            return await cursor.fetchall()

    async def draw_lottery(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT member_id, tickets FROM lottery_contributors')
            contributions = await cursor.fetchall()

            if not contributions:
                return None, 0

            tickets_pool = []
            for member_id, tickets in contributions:
                tickets_pool.extend([member_id] * tickets)

            winner_id = random.choice(tickets_pool)

            cursor = await db.execute('SELECT candy_pot FROM lottery')
            pot = (await cursor.fetchone())[0]

            await db.execute('''
            UPDATE user_data SET candy = candy + ? WHERE member_id = ?
            ''', (pot, winner_id))
            await db.execute('DELETE FROM lottery_contributors')
            await db.execute('UPDATE lottery SET candy_pot = 0')

            await db.commit()

            return winner_id, pot