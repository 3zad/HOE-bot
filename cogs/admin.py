import nextcord
from nextcord.ext import commands
import sys

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.has_permissions(administrator = True)
    @nextcord.slash_command(name="shutdown", description="Turn off the bot")
    async def hello(self, ctx):
        sys.exit(0)