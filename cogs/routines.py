import nextcord
from nextcord.ext import commands
from db.MainDatabase import MainDatabase
from nextcord.ext import commands, tasks
import datetime
from bot_utils.csv_utils import CSVUtils

class Routines(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = MainDatabase()
        self.config = config

        self.reminder_task.start()

    @tasks.loop(seconds=5)
    async def reminder_task(self):
        rows = await self.db.get_all_reminders()
        for row in rows:
            dt_obj = datetime.datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
            time_difference = dt_obj - datetime.datetime.now()

            if time_difference.total_seconds() <= 0:
                channel = self.bot.get_channel(int(row[3]))
                await self.db.delete_reminder_by_start_and_end_time(row[1], row[2])
                await channel.send(f"<@{row[1]}>'s reminder: {row[2]}")

    @reminder_task.before_loop
    async def before_reminder_task(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=300)
    async def csv_task(self):
        start = datetime.time(2,0,0)
        end = datetime.time(2,5,0)
        if start < datetime.datetime.now() < end:
            print("Converting CSV!")
            csv = CSVUtils()
            csv.toCSV()

    @csv_task.before_loop
    async def before_csv_task(self):
        await self.bot.wait_until_ready()

    async def cog_unload(self):
        await self.db.close()

