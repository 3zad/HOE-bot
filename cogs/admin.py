import nextcord
from nextcord.ext import commands
import sys
from db.MainDatabase import MainDatabase

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

    @nextcord.slash_command(name="fetch", description="(Admin command) Fetch content of messages for the database.")
    async def fetch(self, ctx: nextcord.Interaction):
        if ctx.user.id not in self.admins:
            await ctx.response.send_message("You do not have permission to mute members!", ephemeral=True)
            return

        if self.fetching:
            await ctx.response.send_message("Already fetching messages!", ephemeral=True)
            return
        
        self.fetching = True

        while True:
            pass

        await ctx.response.send_message("Done fetching messages!", ephemeral=True)