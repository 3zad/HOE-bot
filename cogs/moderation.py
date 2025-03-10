import nextcord
from nextcord.ext import commands
from db.MainDatabase import MainDatabase

class AdminCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = MainDatabase()
        
        self.config = config
        self.admins = config["owners"]

    @nextcord.slash_command(name="ban", description="(Admin command) Ban user.")
    async def ban(self, ctx, member: nextcord.Member, *, reason="No reason provided"):
        if ctx.user.id in self.admins:
            await member.ban(reason=reason)
            await ctx.send(f"🔨 {member.mention} has been banned for: {reason}")
            
    @nextcord.slash_command(name="kick", description="(Admin command) Kick user.")
    async def kick(self, ctx, member: nextcord.Member, *, reason="No reason provided"):
        if ctx.user.id in self.admins:
            await member.kick(reason=reason)
            await ctx.send(f"🦵 {member.mention} has been kicked for: {reason}")
    
    @nextcord.slash_command(name="warn", description="(Admin command) Warn user.")
    async def warn(self, ctx, member: nextcord.Member, *, reason="No reason provided"):
        if ctx.user.id in self.admins:
            await self.db.add_warning(member.id, reason)
            await ctx.send(f"🚫 {member.mention} has been warned for: {reason}")
    