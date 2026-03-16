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

    # --- Elo --- #

    @nextcord.slash_command(name="elo", description="Calculate a user's elo.")
    @bot_channel_only()
    async def elo(self, ctx, user: nextcord.User):
        elo = await self.db.calculate_elo(user.id)
        await ctx.send(f"{user.mention}'s elo is {elo}")

    @nextcord.slash_command(name="spam", description="Number of times a user has spammed.")
    @bot_channel_only()
    async def spam(self, ctx, user: nextcord.User):
        count = await self.db.number_of_spams(user.id)
        await ctx.send(f"{user.mention} has spammed {count} times.")

    @nextcord.slash_command(name="warning", description="Various warning-related commands.")
    @bot_channel_only()
    async def warning(self, ctx):
        pass

    @warning.subcommand(name="top", description="Show the top 10 users with the most warnings.")
    async def top(self, ctx):
        top_warnings = await self.db.get_top_warnings()
        if not top_warnings:
            await ctx.send("No warnings found.")
            return
    
        embed = nextcord.Embed(title="🚫 Top 10 Users with Most Warnings 🚫", color=nextcord.Color.red())
        for user_id, count in top_warnings:
            user = self.bot.get_user(user_id)
            username = user.name if user else f"User ID {user_id}"
            embed.add_field(name=f"{username}", value=f"{count} warning(s)", inline=False)

        await ctx.send(embed=embed)

    @warning.subcommand(name="count", description="Count warnings for a user.")
    async def count(self, ctx, user: nextcord.User):
        warnings = await self.db.get_warnings(user.id)
        if not warnings:
            await ctx.send(f"{user.mention} has no warnings.")
            return
        
        reasons_str = ""
        count = 0
        for warning in warnings:
            reason = warning[0]
            reasons_str += "- " + reason + "\n"
            count += 1
            if count >= 10:
                reasons_str += f"... and {len(warnings) - count} more."
                break
        
        await ctx.send(f"{user.mention} has {len(warnings)} warning(s).\n{reasons_str}")

    @nextcord.slash_command(name="curse", description="Various curse-related commands.")
    @bot_channel_only()
    async def curse(self, ctx):
        pass

    @curse.subcommand(name="count", description="Count curse words for a user.")
    async def count(self, ctx, user: nextcord.User):
        curse_count, slur_count = await self.db.get_curse_count(user.id)
        await ctx.send(f"{user.mention} has used {curse_count} curse word(s) and {slur_count} slur(s).")

    @curse.subcommand(name="top", description="Show the top 10 users with the most curse words.")
    async def top(self, ctx):
        top_curses = await self.db.get_top_curse_users()
        if not top_curses:
            await ctx.send("No curse words found.")
            return
    
        embed = nextcord.Embed(title="Top 10 Users with Most Curse Words", color=nextcord.Color.dark_red())
        for user_id, curse_count, slur_count in top_curses:
            user = self.bot.get_user(user_id)
            username = user.name if user else f"User ID {user_id}"
            embed.add_field(name=f"{username}", value=f"{curse_count} curse word(s) and {slur_count} slur(s)", inline=False)

        await ctx.send(embed=embed)

    @nextcord.slash_command(name="leaderboard", description="Show the elo leaderboard.")
    @bot_channel_only()
    async def leaderboard(self, ctx):
        leaderboard = await self.db.get_leaderboard(allow_min_or_max_elo=False)
        if not leaderboard:
            await ctx.send("Leaderboard is empty.")
            return
        
        # sort leaderboard by elo in descending order
        leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))
        
        embed = nextcord.Embed(title="🏆 Elo Leaderboard 🏆", color=nextcord.Color.gold())
        halfway_point = len(leaderboard) // 2
        count = 0
        for user_id, elo in leaderboard.items():
            if count == halfway_point:
                embed.add_field(name="...", value="", inline=False)
            user = self.bot.get_user(user_id)
            username = user.name if user else f"User ID {user_id}"
            embed.add_field(name=f"{username}", value=f"{elo} ELO points.", inline=False)
            count += 1

        await ctx.send(embed=embed)
   
    async def cog_unload(self):
        await self.db.close()

