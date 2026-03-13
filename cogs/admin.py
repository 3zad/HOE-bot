import nextcord
from nextcord.ext import commands
import sys
from cogs.__checks import admin_only

class AdminCommands(commands.Cog):
    def __init__(self, bot, config, db):
        self.bot = bot
        self.db = db
        self.config = config

    @nextcord.slash_command(name="shutdown", description="(Admin command) Turn off the bot")
    @admin_only()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down!")
        sys.exit(0)