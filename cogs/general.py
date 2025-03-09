import nextcord
from nextcord.ext import commands
import sqlite3
from langdetect import detect
from db.MainDatabase import MainDatabase
from bot_utils.language import Language

class GeneralCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = MainDatabase()
        self.config = config
        print("GeneralCommands Cog Initialized")


    @nextcord.slash_command(name="test_general", description="Hello")
    async def test_general(self, ctx):
        await ctx.send("The general cog is loaded.")

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        # Basic message statistics
        num_words = len(message.content.split())
        num_exclamations = message.content.count("!")
        num_questions = message.content.count("?")
        num_periods = message.content.count(".")
        num_emojis = sum(1 for char in message.content if char in "😊😂😍🔥💀👍")  # Add more emojis if needed

        language = Language()

        num_curse_words = language.num_curses(message.content)

        if num_words == 0:
            return

        if num_words >= 3:
            try:
                lang = detect(message.content)
            except:
                lang = "unknown"
            
            try:
                if language.is_gibberish(message.content):
                    reading_level = None
                    dale_chall = None
                else:
                    reading_level = language.reading_level(message.content)
                    dale_chall = language.dale_chall(message.content)
                    print("Not gibberish")
            except:
                reading_level = None
                dale_chall = None
        else:
            lang = None
            reading_level = None
            dale_chall = None

        await self.db.add_message(message.author, num_words, num_curse_words, num_questions, num_periods, num_exclamations, num_emojis, lang, reading_level, dale_chall)

        print(f"Processed message from {message.author}: {message.content}")

    async def cog_unload(self):
        await self.db.close()

