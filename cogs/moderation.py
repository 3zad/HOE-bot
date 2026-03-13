import nextcord
from nextcord.ext import commands
import datetime
from cogs.__checks import moderator_only, bot_channel_only

class ModerationCommands(commands.Cog):
    def __init__(self, bot, config, db):
        self.bot = bot
        self.db = db
        self.config = config

    @nextcord.slash_command(name="ban", description="(Admin command) Ban user.")
    @moderator_only()
    async def ban(self, ctx, member: nextcord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} has been banned for: {reason}")
            
    @nextcord.slash_command(name="kick", description="(Admin command) Kick user.")
    @moderator_only()
    async def kick(self, ctx, member: nextcord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.send(f"🦵 {member.mention} has been kicked for: {reason}")
    
    @nextcord.slash_command(name="warn", description="(Admin command) Warn user.")
    @moderator_only()
    async def warn(self, ctx, member: nextcord.Member, *, reason="No reason provided"):
        await self.db.add_warning(member.id, reason, ctx.user.id)
        await ctx.send(f"🚫 {member.mention} has been warned for: {reason}")

    # --- Mute --- #

    @nextcord.slash_command(name="mute", description="Manage muting users.")
    @moderator_only()
    async def mute(self, ctx: nextcord.Interaction):
        pass

    @mute.subcommand(name="add", description="Mute a user for a specific duration.")
    @moderator_only()
    async def mute_add(self, ctx: nextcord.Interaction, member: nextcord.Member, duration: int):
        mute_duration = datetime.timedelta(minutes=duration)
        unmute_time = nextcord.utils.utcnow() + mute_duration

        try:
            await member.edit(timeout=unmute_time)
            await ctx.response.send_message(f"🔇 {member.mention} has been muted for {duration} minutes.")
        except nextcord.Forbidden:
            await ctx.response.send_message("I do not have permission to mute this user.", ephemeral=True)

    @mute.subcommand(name="remove", description="Remove a mute from a user.")
    @moderator_only()
    async def mute_remove(self, ctx: nextcord.Interaction, member: nextcord.Member):
        if not member._timeout:
            await ctx.response.send_message(f"{member.mention} is not muted.", ephemeral=True)
            return

        try:
            await member.edit(timeout=None)
            await ctx.response.send_message(f"🔊 {member.mention} has been unmuted.")
        except nextcord.Forbidden:
            await ctx.response.send_message("I do not have permission to unmute this user.", ephemeral=True)

    @mute.subcommand(name="change", description="Change a mute duration of a user.")
    @moderator_only()
    async def mute_change(self, ctx: nextcord.Interaction, member: nextcord.Member, new_duration: int):
        if not member._timeout:
            await ctx.response.send_message(f"{member.mention} is not muted.", ephemeral=True)
            return

        mute_duration = datetime.timedelta(minutes=new_duration)
        unmute_time = nextcord.utils.utcnow() + mute_duration

        mute_time = int((unmute_time-member._timeout).total_seconds()/60+0.5)

        try:
            await member.edit(timeout=None)
            await member.edit(timeout=unmute_time)
            if mute_time < 0:
                await ctx.response.send_message(f"🔇 {member.mention}'s mute shortened by {-mute_time} minutes.")
            else:
                await ctx.response.send_message(f"🔇 {member.mention}'s mute extended by {mute_time} minutes.")
        except nextcord.Forbidden:
            await ctx.response.send_message("I do not have permission to mute this user.", ephemeral=True)

    @mute.subcommand(name="extend", description="Extend a mute duration of a user.")
    @moderator_only()
    async def mute_extend(self, ctx: nextcord.Interaction, member: nextcord.Member, new_duration: int):
        if not member._timeout:
            await ctx.response.send_message(f"{member.mention} is not muted.", ephemeral=True)
            return

        mute_duration = datetime.timedelta(minutes=new_duration)
        remaining_time = member._timeout - nextcord.utils.utcnow()
        unmute_time = remaining_time + mute_duration

        try:
            await member.edit(timeout=None)
            await member.edit(timeout=unmute_time)
            await ctx.response.send_message(f"🔇 {member.mention}'s mute extended by {new_duration} minutes.")
        except nextcord.Forbidden:
            await ctx.response.send_message("I do not have permission to mute this user.", ephemeral=True)
    
    @mute.subcommand(name="remaining", description="Get the remaining duration of a member's mute.")
    @bot_channel_only()
    async def mute_remaining(self, ctx: nextcord.Interaction, member: nextcord.Member):
        try:
            member = await ctx.guild.fetch_member(member.id)

            if hasattr(member, "_timeout") and member._timeout:
                remaining = member._timeout - nextcord.utils.utcnow()
                if remaining.total_seconds() > 0:
                    await ctx.response.send_message(
                        f"🔇 {member.mention} is muted for another {remaining}."
                    )
                else:
                    await ctx.response.send_message(
                        f"{member.mention} is no longer muted."
                    )
            else:
                await ctx.response.send_message(
                    f"{member.mention} is not muted."
                )
        except nextcord.NotFound:
            await ctx.response.send_message("User not found.")
        except Exception as e:
            await ctx.response.send_message(f"Error: {e}")