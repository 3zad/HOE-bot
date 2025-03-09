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
                language TEXT,
                user_id_sent INTEGER,
                user_id_recieved INTEGER,
                reaction_emoji TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id_sent) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id_recieved) REFERENCES users(user_id) ON DELETE CASCADE
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS vc (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                joined_at TIMESTAMP,
                joined_left TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
                '''
            )

            await db.commit()


    # -------------- User Statistics -------------- #

    # --- Set --- #
    async def add_message(self, user, word_count, curse_count, question_count, period_count, exclaimation_count, emoji_count, language, reading_level, dale_chall):
        """Hello"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO messages (user_id, number_of_words, number_of_curse_words, number_of_question_marks, number_of_periods, number_of_exclaimation_marks, number_of_emojis, language, reading_level, dale_chall)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(user), word_count, curse_count, question_count, period_count, exclaimation_count, emoji_count, language, reading_level, dale_chall))
            await db.commit()

    # --- Get --- #
    async def get_number_of_words_and_rows(self, user):
        """Retrieve data for a specific user."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT SUM(number_of_words), COUNT(*) FROM messages WHERE user_id = ?', (str(user),))
            row = await cursor.fetchone()
            print(row)
            return row