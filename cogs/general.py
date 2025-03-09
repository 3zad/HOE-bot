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

    @nextcord.slash_command(name="word_count", description="Gives information on the number of words from a user.")
    async def word_count(self, ctx, member):
        word_tuple = await self.db.get_message_sums(member[2:-1])
        await ctx.send(f"User {member} has sent {int(word_tuple[1])} words over {int(word_tuple[0])} messages. The average word count per message is {round(float(word_tuple[1])/float(word_tuple[0]), 2)} words.")

    @nextcord.slash_command(name="curse_count", description="Gives information on the number of curse words from a user.")
    async def curse_count(self, ctx, member):
        word_tuple = await self.db.get_message_sums(member[2:-1])
        await ctx.send(f"User {member} has sent {int(word_tuple[2])} curse words over {int(word_tuple[0])} messages. The average curse word count per message is {round(float(word_tuple[2])/float(word_tuple[0]), 2)} curse words.")

    @nextcord.slash_command(name="language", description="Gives language information about a user.")
    async def language(self, ctx, member):
        language_row = await self.db.get_language(member[2:-1])
        language_dict = {}
        summa = 0
        for ln in language_row:
            ln = ln[0]
            if ln == None or ln == "None":
                continue
            
            if ln in language_dict:
                language_dict[ln] += 1
            else:
                language_dict[ln] = 1

            summa += 1
        
        sorted_items = sorted(language_dict.items(), key=lambda x: x[1], reverse=True)

        first_largest_key = sorted_items[0][0] if len(sorted_items) > 1 else None
        second_largest_key = sorted_items[1][0] if len(sorted_items) > 1 else None
        third_largest_key = sorted_items[2][0] if len(sorted_items) > 2 else None

        first = round(language_dict[first_largest_key]/summa*100,2)
        second = round(language_dict[second_largest_key]/summa*100,2)
        third = round(language_dict[third_largest_key]/summa*100,2)

        persum = round(100-(first+second+third),2)

        await ctx.send(f"User {member}'s messages are {first}% {first_largest_key}, {second}% {second_largest_key}, {third}% {third_largest_key}, and {persum}% other.")



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

