import aiosqlite
from datetime import datetime
from typing import Tuple, List
import math

class MainDatabase:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MainDatabase, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config, language, db_name="main.db"):
        self.db_name = db_name
        self.config = config
        self.language = language


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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                channel_id INTEGER,
                message_id INTEGER,
                message_content TEXT,
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
                issuer INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                FOREIGN KEY (issuer) REFERENCES users(user_id) ON DELETE CASCADE
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                reminder TEXT,
                channel_id INTEGER,
                end_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
                '''
            )

            await db.execute(
                '''
                CREATE TABLE IF NOT EXISTS leaderboard (
                user_id INTEGER PRIMARY KEY,
                elo REAL
                );
                '''
            )

            await db.commit()

    # -------------- CSV -------------- #
    async def to_CSV(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id, channel_id, message_content FROM messages WHERE message_content is not null')
            row = await cursor.fetchall()
            return row

    # -------------- Reminders -------------- #

    # --- Set --- #

    async def add_reminder(self, user, reminder, channel_id, end_time):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO reminders (user_id, reminder, channel_id, end_at)
                VALUES (?, ?, ?, ?)
            ''', (int(user), reminder, int(channel_id), end_time))
            await db.commit()

    async def delete_reminder_by_start_and_end_time(self, user_id, reminder):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                DELETE FROM reminders WHERE user_id = ? AND reminder = ?;
            ''', (user_id, reminder))
            await db.commit()

    # --- Get --- #

    async def get_all_reminders(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM reminders')
            rows = await cursor.fetchall()
            return rows

    # -------------- Moderation -------------- #
    
    # --- Set --- #
    
    async def add_warning(self, user, reason, issuer_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO warnings (user_id, reason, issuer)
                VALUES (?, ?, ?)
            ''', (str(user), reason, str(issuer_id)))
            await db.commit()


    # -------------- User Statistics -------------- #

    # --- Set --- #
    async def add_message(self, user, channel_id, message_id, message_content):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO messages (user_id, channel_id, message_id, message_content)
                VALUES (?, ?, ?, ?)
            ''', (str(user), channel_id, message_id, message_content))
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
    async def get_warning_rankings(self):
        """Get top 5 people with the most warnings."""
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id, COUNT(user_id) AS warning_count FROM warnings GROUP BY user_id ORDER BY warning_count DESC LIMIT 5')
            row = await cursor.fetchall()
            return row
        
    async def get_number_of_warnings(self, user) -> int:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT COUNT(*) FROM warnings WHERE user_id = ?', (str(user),))
            row = await cursor.fetchone()
            return int(row[0]) if row else 0
    
    async def is_starred_enough(self, message_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''SELECT COUNT(*) FROM reactions WHERE message_id = ? AND reaction_emoji = '⭐' AND add_or_remove='add';''', (str(message_id),))
            added = await cursor.fetchone()
            cursor = await db.execute('''SELECT COUNT(*) FROM reactions WHERE message_id = ? AND reaction_emoji = '⭐' AND add_or_remove='remove';''', (str(message_id),))
            removed = await cursor.fetchone()
            
            if added[0]-removed[0] >= 5:
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
            SELECT 
                strftime('%H', created_at) AS hour, 
                COUNT(*) AS message_count,
                (julianday('now') - julianday(MIN(created_at))) AS days_since_earliest
            FROM messages
            WHERE created_at IS NOT NULL
            GROUP BY hour
            ORDER BY hour;
            """)
            output = await cursor.fetchall()
            return output
        
    # --- DB migration n shiet --- #    
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
            
    async def migrate(self) -> None:
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("ALTER TABLE messages DROP COLUMN number_of_words;")
            await db.execute("ALTER TABLE messages DROP COLUMN number_of_curse_words;")
            await db.execute("ALTER TABLE messages DROP COLUMN number_of_question_marks;")
            await db.execute("ALTER TABLE messages DROP COLUMN number_of_periods;")
            await db.execute("ALTER TABLE messages DROP COLUMN number_of_exclaimation_marks;")
            await db.execute("ALTER TABLE messages DROP COLUMN number_of_emojis;")
            await db.execute("ALTER TABLE messages DROP COLUMN language;")
            await db.execute("ALTER TABLE messages DROP COLUMN reading_level;")
            await db.execute("ALTER TABLE messages DROP COLUMN dale_chall;")
            await db.commit()


    # --- Elo --- #

    async def generate_leaderboard(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT DISTINCT user_id FROM messages')
            row = await cursor.fetchall()
            count = 0
            for user in row:
                count += 1
                print(f"({count}/{len(row)}) Calculating elo for user {user[0]}...")
                user_id = user[0]
                elo = await self.calculate_elo(user_id)
                await db.execute('INSERT OR REPLACE INTO leaderboard (user_id, elo) VALUES (?, ?)', (str(user_id), elo))
                await db.commit()

    async def get_leaderboard(self, n=5, allow_min_or_max_elo=True):
        async with aiosqlite.connect(self.db_name) as db:
            user_elo: dict = {}
            for label in ["ASC", "DESC"]:
                if not allow_min_or_max_elo:
                    cursor = await db.execute(f'SELECT user_id, elo FROM leaderboard WHERE elo > 0 AND elo < 100 ORDER BY elo {label} LIMIT ?', (n,))
                else:
                    cursor = await db.execute(f'SELECT user_id, elo FROM leaderboard ORDER BY elo {label} LIMIT ?', (n,))
                row = await cursor.fetchall()
                for user in row:
                    user_id = user[0]
                    elo = user[1]
                    user_elo[user_id] = elo
            return user_elo
        

    async def get_curse_count(self, user_id) -> Tuple[int, int]:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT message_content FROM messages WHERE user_id = ?', (str(user_id),))
            row = await cursor.fetchall()
            curse_count = 0
            slur_count = 0
            for message in row:
                message_content = message[0]
                curse_count += self.language.number_of_curse_words(message_content)
                slur_count += self.language.number_of_really_bad_curse_words(message_content)
            return curse_count, slur_count
    
    async def get_top_curse_users(self, n=10) -> list[Tuple[int, int, int]]:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT user_id, message_content FROM messages')
            row = await cursor.fetchall()
            user_curse_counts = {}
            user_slur_counts = {}
            for message in row:
                user_id = message[0]
                message_content = message[1]
                curse_count = self.language.number_of_curse_words(message_content)
                slur_count = self.language.number_of_really_bad_curse_words(message_content)
                user_curse_counts[user_id] = user_curse_counts.get(user_id, 0) + curse_count
                user_slur_counts[user_id] = user_slur_counts.get(user_id, 0) + slur_count
            top_users = sorted(user_curse_counts.items(), key=lambda x: x[1], reverse=True)[:n]
            return [(user_id, curse_count, user_slur_counts.get(user_id, 0)) for user_id, curse_count in top_users]

    async def calculate_elo(self, user_id):
        """
        User's elo is calculated based on the number of messages, 
        the number of curse words, and the number of warnings. The 
        more messages and the fewer curse words/warnings, the higher the elo.
        """
        # x = number of chars in a message
        # y = number of curses in a message
        curse_calc = lambda x, y, z: max(0, 100*(1-((self.config.config["elo"]["curse_multiplier"]*y + self.config.config["elo"]["slur_multiplier"]*z)/x)))
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT message_content FROM messages WHERE user_id = ?', (str(user_id),))
            row = await cursor.fetchall()
            elo = 0
            count = 0
            for message in row:
                message_content = message[0]
                if len(message_content) == 0:
                    continue
                
                num_curses = self.language.number_of_curse_words(message_content)
                num_really_bad_curses = self.language.number_of_really_bad_curse_words(message_content)
                count += 1
                elo += curse_calc(len(message_content), num_curses, num_really_bad_curses)

            if count == 0:
                return 0
            
            elo_avg = elo / count

            num_spams = await self.number_of_spams(user_id)
            # 1 spam every 100 messages allowed
            if num_spams > 0:
                num_messages_between_spams = count / max(1, num_spams)
                # Linear penalty because before there were crazy drop offs
                spam_ratio = min(1.0, num_messages_between_spams / 100)
                spam_penalty = max(0.1, 1.0 - (1.0 - spam_ratio) * self.config.config["elo"]["spam_multiplier"])
                elo_avg *= spam_penalty

            num_warnings = await self.get_number_of_warnings(user_id)
            warning_penalty = num_warnings * self.config.config["elo"]["warning_multiplier"]
            elo_avg = max(0, elo_avg - warning_penalty)

            time_since_first_message_in_seconds = await self.time_since_first_message(user_id)
            max_possible_elo = lambda x: 100 * (1-(pow(math.e, -0.000005*x)))
            elo_avg = elo_avg*(max_possible_elo(time_since_first_message_in_seconds)/100)

            time_since_last_message_in_seconds = await self.time_since_last_message(user_id)
            # every day of inactivity reduces elo by 10%
            inactivity_penalty = pow(0.9, time_since_last_message_in_seconds / 86400)
            elo_avg *= inactivity_penalty

            gaps = await self.get_message_gaps(user_id, 3)
            # every gap of 3 days reduces elo by 5%, every gap of 7 days reduces elo by 30%
            for gap in gaps:
                if gap >= 7:
                    elo_avg *= 0.7
                elif gap >= 3:
                    elo_avg *= 0.95

            return round(elo_avg, 2)
        
    async def time_since_first_message(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT created_at FROM messages WHERE user_id = ? ORDER BY created_at ASC LIMIT 1', (str(user_id),))
            row = await cursor.fetchone()
            if row is None:
                return 0  # If user has no messages, return 0 time
            first_message_time = row[0]
            first_message_time = datetime.strptime(first_message_time, "%Y-%m-%d %H:%M:%S")
            return int((datetime.now() - first_message_time).total_seconds())
    
    async def time_since_last_message(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT created_at FROM messages WHERE user_id = ? ORDER BY created_at DESC LIMIT 1', (str(user_id),))
            row = await cursor.fetchone()
            if row is None:
                return 0  # If user has no messages, return 0 time
            last_message_time = row[0]
            last_message_time = datetime.strptime(last_message_time, "%Y-%m-%d %H:%M:%S")
            return int((datetime.now() - last_message_time).total_seconds())
        
    async def get_message_gaps(self, user_id, days) -> List[int]:
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT created_at FROM messages WHERE user_id = ? ORDER BY created_at ASC', (str(user_id),))
            row = await cursor.fetchall()
            message_times = [datetime.strptime(message[0], "%Y-%m-%d %H:%M:%S") for message in row]
            gaps = []
            for i in range(1, len(message_times)):
                gap = (message_times[i] - message_times[i-1]).total_seconds() / 86400
                if gap >= days:
                    gaps.append(gap)
            return gaps
        
    async def number_of_spams(self, user_id):
        # 3 messages sent within 0.8 of each other
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute("""
                SELECT COUNT(*) AS spam_instances
                FROM (
                    SELECT
                        created_at,
                        LAG(created_at, 1) OVER (
                            PARTITION BY user_id
                            ORDER BY created_at
                        ) AS prev_created_at,
                        LAG(created_at, 2) OVER (
                            PARTITION BY user_id
                            ORDER BY created_at
                        ) AS prev_prev_created_at
                    FROM messages
                    WHERE user_id = ?
                )
                WHERE prev_prev_created_at IS NOT NULL
                    AND ABS(strftime('%s', created_at) - strftime('%s', prev_prev_created_at)) <= 0.8;
            """, (str(user_id),))
            
            row = await cursor.fetchone()
            return int(row[0]) if row else 0