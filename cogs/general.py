import nextcord
from nextcord.ext import commands
import matplotlib.pyplot as plt
import io
from langdetect import detect
from db.MainDatabase import MainDatabase
from bot_utils.language import Language

class GeneralCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = MainDatabase()
        self.config = config

        if config["mode"] == "production":
            self.star_channel = self.config["star_channel"]
        else:
            self.star_channel = self.config["star_channel_testing"]


    async def star_embed(self, guild_id, channel_id, message_id, message, member):
        user = await self.bot.fetch_user(member)

        title = f"Starred message by {user}"

        url = f"https://discord.com/channels/{str(guild_id)}/{str(channel_id)}/{str(message_id)}"
        print(url)

        embed = nextcord.Embed(colour=nextcord.colour.Colour.yellow(), color=None, title=title, type='rich', url=url, description=message, timestamp=None)
        try:
            user = await self.bot.fetch_user(member)
            embed.set_thumbnail(url=user.avatar)
        except:
            pass
        return embed

    @nextcord.slash_command(name="word_count", description="Gives information on the number of words from a user.")
    async def word_count(self, ctx, member):
        word_tuple = await self.db.get_message_sums(member[2:-1])
        await ctx.send(f"User {member} has sent {int(word_tuple[1])} words over {int(word_tuple[0])} messages. The average word count per message is {round(float(word_tuple[1])/float(word_tuple[0]), 2)} words.")

    @nextcord.slash_command(name="curse_count", description="Gives information on the number of curse words from a user.")
    async def curse_count(self, ctx, member):
        word_tuple = await self.db.get_message_sums(member[2:-1])
        await ctx.send(f"User {member} has sent {int(word_tuple[2])} curse words over {int(word_tuple[0])} messages. The average curse word count per message is {round(float(word_tuple[2])/float(word_tuple[0]), 2)} curse words.")

    @nextcord.slash_command(name="server_curse_count", description="Gives information on the number of curse words for the server.")
    async def server_curse_count(self, ctx):
        word_tuple = await self.db.get_message_sums_of_server()
        await ctx.send(f"{int(word_tuple[2])} curse words were sent over {int(word_tuple[0])} messages. The average curse word count per message is {round(float(word_tuple[2])/float(word_tuple[0]), 2)} curse words.")


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

    @nextcord.slash_command(name="reading_level", description="Gives the average reading level of a user.")
    async def reading_level(self, ctx, member):
        word_tuple = await self.db.get_reading_level_sums(member[2:-1])
        await ctx.send(f"User {member} has a reading level of {word_tuple[0]} and a dale-chall readability level of {word_tuple[1]}.")

    @nextcord.slash_command(name="server_reading_level", description="Gives the average reading level of the whole server.")
    async def server_reading_level(self, ctx):
        word_tuple = await self.db.get_reading_level_sums_of_server()
        await ctx.send(f"The global reading level is {word_tuple[0]} and the global dale-chall readability level is {word_tuple[1]}.")

    @nextcord.slash_command(name="top_reading_level", description="Returns the user who has the highest reading level.")
    async def top_reading_level(self, ctx):
        word_tuple = await self.db.get_highest_reading_level()
        member = await self.bot.fetch_user(int(word_tuple[0]))
        await ctx.send(f"The user with the highest reading level is {member} with a score of {word_tuple[1]}.")

    @nextcord.slash_command(name="bottom_reading_level", description="Returns the user who has the lowest reading level.")
    async def bottom_reading_level(self, ctx):
        word_tuple = await self.db.get_lowest_reading_level()
        member = await self.bot.fetch_user(int(word_tuple[0]))
        await ctx.send(f"The user with the lowest reading level is {member} with a score of {word_tuple[1]}.")

    @nextcord.slash_command(name="message_times", description="Outputs a graph with the number of messages during different times of the day.")
    async def message_times(self, ctx):
        data = await self.db.get_message_time_counts()
        hours = [int(row[0]) for row in data]
        message_counts = [row[1]/row[2] for row in data]

        all_hours = list(range(24))
        message_counts_full = [message_counts[hours.index(h)] if h in hours else 0 for h in all_hours]

        plt.figure(figsize=(10, 5))
        plt.bar(all_hours, message_counts_full, color='blue', alpha=0.7)
        plt.xticks(range(24))  # Show all 24 hours
        plt.xlabel("Hour of the Day (GMT)")
        plt.ylabel("Number of Messages")
        plt.title("Average Messages Sent Per Hour")
        plt.grid(axis='y', linestyle='--', alpha=0.6)

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        await ctx.send(file=nextcord.File(buf, "messages_per_hour.png"))

   
    async def cog_unload(self):
        await self.db.close()

