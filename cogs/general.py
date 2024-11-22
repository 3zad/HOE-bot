import nextcord
from nextcord.ext import commands

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    @commands.Cog.listener()
    async def on_message(self, member):
        print("here")
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'{member.mention} just sent a message!')

    @nextcord.slash_command(name="hello", description="test")
    async def hello(self, ctx):
        """Says hello"""
        print(ctx.user.id)
        await ctx.response.send_message("hello")