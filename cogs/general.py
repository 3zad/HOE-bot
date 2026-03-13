import nextcord
from nextcord.ext import commands
import matplotlib.pyplot as plt
import datetime
import io
from cogs.__checks import bot_channel_only

class GeneralCommands(commands.Cog):
    def __init__(self, bot, config, db):
        self.bot = bot
        self.db = db
        self.config = config

        self.star_channel: int = self.config.config["star_channel"]

        self.bot_channels: list = self.config.config["bot_channels"]

    @nextcord.slash_command(name="count", description="Various count commands.")
    @bot_channel_only()
    async def count(self, ctx: nextcord.Interaction):
        pass

    @count.subcommand(name="word", description="Gives information on the number of words from a user.")
    @bot_channel_only()
    async def word_count(self, ctx, member):
        await ctx.send(f"Not implemented.")

    @count.subcommand(name="curse", description="Gives information on the number of curse words from a user.")
    @bot_channel_only()
    async def curse_count(self, ctx, member):
        await ctx.send(f"Not implemented.")

    @count.subcommand(name="servercurse", description="Gives information on the number of curse words for the server.")
    @bot_channel_only()
    async def server_curse_count(self, ctx):
        await ctx.send(f"Not implemented.")

    @nextcord.slash_command(name="message_times", description="Outputs a graph with the number of messages during different times of the day.")
    @bot_channel_only()
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

    @nextcord.slash_command(name="reminder", description="DAY-MONTH-YEAR HOUR:MINUTE:SECOND gives a reminder after a period of time.")
    @bot_channel_only()
    async def reminder(self, ctx: nextcord.Interaction, reminder, year_month_day, hour_minute_second):
        date_format = "%Y-%m-%d %H:%M:%S"
        date_str = f"{year_month_day} {hour_minute_second}"
        
        try:
            date_obj = datetime.datetime.strptime(date_str, date_format)
            
            if (date_obj - datetime.datetime.now()).total_seconds() < 300:
                await ctx.response.send_message("Please set a time that is more than 5 minutes in the future.", ephemeral=True)
                return
        except ValueError:
            await ctx.response.send_message("Make sure single-digit days and months are padded with 0s. For example, 2025-3-4 (4rd of March 2025) should be written as 2025-03-04.", ephemeral=True)
            return

        for char in reminder:
            if char in ["'", '"', '`']:
                await ctx.response.send_message(f"""For security purposes, please refrain from using these characters: ', ", and `.""", ephemeral=True)
                return

        await self.db.add_reminder(ctx.user.id, reminder, ctx.channel.id, date_obj)

        await ctx.response.send_message(f"✅ Reminder set for {date_obj}.")

    @nextcord.slash_command(name="warnings", description="See top 5 people")
    @bot_channel_only()
    async def warnings(self, ctx: nextcord.Interaction):        
        ranking = await self.db.get_warning_rankings()
        print(ranking)

        embed=nextcord.Embed(
                title=f"Users with the most warnings",
                color=nextcord.colour.Colour.green()
        )
        embed.add_field(name="Number of warnings    User", value="", inline=False)

        results_list = []
        for rank in ranking:
            result_line = (
                f"{rank[1]} <@{rank[0]}>"
            )
            results_list.append(result_line)

        if results_list == []:
            await ctx.response.send_message("No results.", ephemeral=True)
            return

        results_text = "\n".join(results_list)
        embed.add_field(name="\u200b", value=results_text, inline=False) 

        await ctx.send(embed=embed)

   
    async def cog_unload(self):
        await self.db.close()

