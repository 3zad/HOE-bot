import aiosqlite
from datetime import datetime
import random

class MainDatabase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MainDatabase, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_name="main.db"):
        self.db_name = db_name

    async def initialize(self):
        """Initialize the database by creating the necessary table."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT
                );

            ''')

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                number_of_words INTEGER,
                number_of_curse_words INTEGER,
                number_of_question_marks INTEGER,
                number_of_periods INTEGER,
                number_of_exclaimation_marks INTEGER,
                number_of_emojis INTEGER,
                language TEXT,
                reading_level REAL,
                dale_chall REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY,
                message_id TEXT,
                user_id_sent INTEGER,
                user_id_recieved INTEGER,
                reaction_emoji TEXT,
                add_or_remove TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id_sent) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id_recieved) REFERENCES users(user_id) ON DELETE CASCADE
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS starred (
                id INTEGER PRIMARY KEY,
                message_id TEXT,
                user_id TEXT,
                FOREIGN KEY (message_id) REFERENCES users(message_id) ON DELETE CASCADE
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS vc (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                joined_at TIMESTAMP,
                left_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
                '''
            )
            
            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
                '''
            )

            await db.commit()

    # -------------- Moderation -------------- #
    
    # --- Set --- #
    
    async def add_warning(self, user, reason):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO warnings (user_id, reason)
                VALUES (?, ?)
            ''', (str(user), reason))
            await db.commit()


    # -------------- User Statistics -------------- #

    # --- Set --- #
    async def add_message(self, user, word_count, curse_count, question_count, period_count, exclaimation_count, emoji_count, language, reading_level, dale_chall):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO messages (user_id, number_of_words, number_of_curse_words, number_of_question_marks, number_of_periods, number_of_exclaimation_marks, number_of_emojis, language, reading_level, dale_chall)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(user), word_count, curse_count, question_count, period_count, exclaimation_count, emoji_count, language, reading_level, dale_chall))
            await db.commit()

    async def set_reaction(self, message_id, user_sent, user_recieved, reaction, is_add):
        if is_add:
            add_or_remove = "add"
        else:
            add_or_remove = "remove"

        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO reactions (message_id, user_id_sent, user_id_recieved, reaction_emoji, add_or_remove)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(message_id), str(user_sent), str(user_recieved), reaction, add_or_remove))
            await db.commit()

    async def add_starred_message(self, message_id, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO starred (message_id, user_id)
                VALUES (?, ?)
            ''', (str(message_id), str(user_id)))
            await db.commit()

    # --- Get --- #
    async def get_message_sums(self, user):
        """Retrieve word data for a specific user."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*), SUM(number_of_words), SUM(number_of_curse_words), SUM(number_of_question_marks), SUM(number_of_periods), SUM(number_of_exclaimation_marks), SUM(number_of_emojis) FROM messages WHERE user_id = ?', (str(user),))
            row = await cursor.fetchone()
            return row
        
    async def get_reading_level_sums(self, user):
        """Retrieve word data for a specific user."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT AVG(reading_level), AVG(dale_chall) FROM messages WHERE user_id = ?', (str(user),))
            row = await cursor.fetchone()
            return row
        
    async def get_reading_level_sums_of_server(self):
        """Retrieve word data globally."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT AVG(reading_level), AVG(dale_chall) FROM messages')
            row = await cursor.fetchone()
            return row
        
    async def get_highest_reading_level(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id, AVG(reading_level) as keskmine FROM messages group by user_id order by keskmine desc')
            row = await cursor.fetchone()
            return row
        
    async def get_lowest_reading_level(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id, AVG(reading_level) as keskmine FROM messages group by user_id order by keskmine asc')
            row = await cursor.fetchone()
            return row
        
    async def get_message_sums_of_server(self):
        """Retrieve word data for a specific user."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*), SUM(number_of_words), SUM(number_of_curse_words), SUM(number_of_question_marks), SUM(number_of_periods), SUM(number_of_exclaimation_marks), SUM(number_of_emojis) FROM messages')
            row = await cursor.fetchone()
            return row

    async def get_language(self, user):
        """Retrieve language data for a specific user."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT language FROM messages WHERE user_id = ?', (str(user),))
            row = await cursor.fetchall()
            return row
        
    async def is_starred_enough(self, message_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''SELECT COUNT(*) FROM reactions WHERE message_id = ? AND reaction_emoji = '⭐' AND add_or_remove='add';''', (str(message_id),))
            added = await cursor.fetchone()
            cursor = await db.execute('''SELECT COUNT(*) FROM reactions WHERE message_id = ? AND reaction_emoji = '⭐' AND add_or_remove='remove';''', (str(message_id),))
            removed = await cursor.fetchone()
            
            if added[0]-removed[0] >= 0:
                return True
            return False
        
    async def is_starred_message(self, message_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''SELECT COUNT(*) FROM starred WHERE message_id = ?;''', (str(message_id),))
            starred = await cursor.fetchone()
            
            if starred[0] == 0:
                return False
            return True
   
    async def get_message_time_counts(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute("""
            SELECT strftime('%H', created_at) AS hour, COUNT(*) AS message_count
            FROM messages
            WHERE created_at IS NOT NULL
            GROUP BY hour
            ORDER BY hour;
            """)
            output = await cursor.fetchall()
            return output
        
    # --- DB migration n shiet --- #
    @DeprecationWarning
    async def drop_reaction_table(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('DROP TABLE reactions;')
            await db.commit()
    
    @DeprecationWarning
    async def drop_starred_table(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('DROP TABLE starred;')
            await db.commit()
    
    async def raw_sql(self, string):
        async with aiosqlite.connect(self.db_name) as db:
            if "select" in string.lower():
                cursor = await db.execute(string)
                row = await cursor.fetchall()
                message = ""
                for item in row:
                    message += str(item) + "\n"
                return message
            else:
                await db.execute(string)
                await db.commit()
                return None