import nextcord
from cogs.general import GeneralCommands
from cogs.admin import AdminCommands
from cogs.moderation import ModerationCommands
from cogs.listeners import Listeners
from cogs.database_commands import DbCommands
from cogs.routines import Routines
import json

intents = nextcord.Intents.all()
intents.message_content = True
intents.reactions = True
intents.voice_states = True
intents.bans = True
intents.members = True

client = nextcord.ext.commands.Bot(command_prefix="owurghoerubheoruihoeb", intents=intents)

with open("config.json", 'r', encoding="UTF-8") as f:
    config = json.load(f)

client.add_cog(GeneralCommands(client, config))
client.add_cog(Listeners(client, config))
client.add_cog(Routines(client, config))
client.add_cog(DbCommands(client, config))
client.add_cog(ModerationCommands(client, config))
client.add_cog(AdminCommands(client, config))


if config["mode"] == "production":
    client.run(open("token.txt", 'r').readline().replace("\n", ""))
else:
    client.run(open("token2.txt", 'r').readline().replace("\n", ""))