import nextcord
from nextcord.ext import commands
from db.MainDatabase import MainDatabase
from datetime import timedelta

class ModerationCommands(commands.Cog):
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
            await self.db.add_warning(member.id, reason, ctx.user.id)
            await ctx.send(f"🚫 {member.mention} has been warned for: {reason}")

    @nextcord.slash_command(name="mute", description="Mutes a user for a certain duration.")
    async def mute(self, ctx: nextcord.Interaction, 
                   member: nextcord.Member, 
                   duration: int, 
                   reason: str = "No reason provided"):
        
        if not ctx.user.id in self.admins:
            await ctx.response.send_message("You do not have permission to mute members!", ephemeral=True)
            return
        
        mute_time = timedelta(minutes=duration)

        try:
            await member.edit(timeout=nextcord.utils.utcnow() + mute_time, reason=reason)
            await ctx.response.send_message(f"🔇 {member.mention} has been muted for {duration} minutes. Reason: {reason}")
        except nextcord.Forbidden:
            await ctx.response.send_message("I do not have permission to mute this user.", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"An error occurred: {e}", ephemeral=True)
    