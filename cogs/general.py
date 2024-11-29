import nextcord
from nextcord.ext import commands

class GeneralCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config