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

    @nextcord.slash_command(name="word_count", description="Hello")
    async def word_count(self, ctx, member):
        word_tuple = await self.db.get_number_of_words_and_rows(member[2:-1])
        await ctx.send(f"User {member} has sent {int(word_tuple[0])} over {int(word_tuple[1])} messages. The average word count per message is {round(float(word_tuple[0])/float(word_tuple[1]), 2)} words.")

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        # Basic message statistics
        num_words = len(message.content.split())
        num_exclamations = message.content.count("!")
        num_questions = message.content.count("?")
        num_periods = message.content.count(".")

        language = Language()

        num_emojis = language.num_emojis(message.content)
        num_curse_words = language.num_curses(message.content)

        if num_words == 0:
            return

        lang = None
        reading_level = None
        dale_chall = None

        if num_words >= 3:
            try:
                lang = detect(message.content)
            except:
                pass
            
            try:
                if not language.is_gibberish(message.content):
                    reading_level = language.reading_level(message.content)
                    dale_chall = language.dale_chall(message.content)
                    print("Not gibberish")
            except:
                pass

        await self.db.add_message(message.author.id, num_words, num_curse_words, num_questions, num_periods, num_exclamations, num_emojis, lang, reading_level, dale_chall)

        print(f"Processed message from {message.author}: {message.content}")

    async def cog_unload(self):
        await self.db.close()

