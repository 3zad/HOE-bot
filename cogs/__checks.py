import nextcord
from nextcord.ext.application_checks import check
from config import Config

conf = Config()

def bot_channel_only():
    async def predicate(interaction: nextcord.Interaction):
        if interaction.channel_id not in conf.config["bot_channels"]:
            await interaction.response.send_message("❌ You can only use bot commands in the bot channel.", ephemeral=True)
            return False
        return True
    return check(predicate)

def admin_only():
    async def predicate(interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need to be an administrator to use this command.", ephemeral=True)
            return False
        return True
    return check(predicate)

def moderator_only():
    async def predicate(interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.moderate_members and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need to be a moderator or administrator to use this command.", ephemeral=True)
            return False
        return True
    return check(predicate)

def dev_only():
    async def predicate(interaction: nextcord.Interaction):
        if int(interaction.user.id) != 740986064314826822:
            await interaction.response.send_message("❌ You need to be a developer to use this command.", ephemeral=True)
            return False
        return True
    return check(predicate)