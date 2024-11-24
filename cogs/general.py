import nextcord
from nextcord.ext import commands

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None