import nextcord
from cogs.general import GeneralCommands
#from cogs.christmas import ChristmasCommands
from cogs.admin import AdminCommands
import json

intents = nextcord.Intents.all()
intents.message_content = True
intents.reactions = True
intents.voice_states = True

client = nextcord.ext.commands.Bot(command_prefix="owurghoerubheoruihoeb", intents=intents)

with open("config.json", 'r', encoding="UTF-8") as f:
    config = json.load(f)

client.add_cog(GeneralCommands(client, config))
client.add_cog(AdminCommands(client, config))

# DO not uncomment
#client.add_cog(ChristmasCommands(client, config))


if config["mode"] == "production":
    client.run(open("token.txt", 'r').readline())
else:
    client.run(open("token2.txt", 'r').readline())