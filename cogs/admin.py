import nextcord
from nextcord.ext import commands
import sys
from db.MainDatabase import MainDatabase
from bot_utils.csv_utils import CSVUtils

class AdminCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = MainDatabase()
        
        self.config = config
        self.admins = config["owners"]

        self.fetching = False

    @nextcord.slash_command(name="shutdown", description="(Admin command) Turn off the bot")
    async def shutdown(self, ctx):
        if ctx.user.id in self.admins:
            await ctx.send("Shutting down!")
            sys.exit(0)

    @nextcord.slash_command(name="csv", description="(Admin command) Export data.")
    async def csv(self, ctx):
        if ctx.user.id not in self.admins:
            await ctx.response.send_message("Admins only", ephemeral=True)
        
        status_message = await ctx.channel.send("Starting CSV dump...")

        csv = CSVUtils()
        await csv.to_csv()

        await status_message.edit(content=f"Complete!")
        await ctx.response.send_message("Converting is complete", ephemeral=True)

    @nextcord.slash_command(name="process", description="(Admin command) Process data.")
    async def process(self, ctx, min_support: float):
        if ctx.user.id not in self.admins:
            await ctx.response.send_message("Admins only", ephemeral=True)
        
        await ctx.response.defer()
        status_message = await ctx.followup.send("Starting processing with IDs...")

        csv = CSVUtils()
        await csv.process_data(min_support=0.0012)

        await status_message.edit(content=f"Starting processing without IDs...")
        await csv.process_data_no_id(min_support=min_support)

        await status_message.edit(content=f"Complete!")
        await ctx.followup.send("Processing is complete", ephemeral=True)