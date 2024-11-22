import nextcord
from cogs.general import GeneralCommands
from cogs.christmas import ChristmasCommands
from cogs.admin import AdminCommands
from db.Database import Database

intents = nextcord.Intents.all()
intents.message_content = True



client = nextcord.Client(intents=intents)

client.add_cog(GeneralCommands(client))
client.add_cog(ChristmasCommands(client))
client.add_cog(AdminCommands(client))

client.run(open("token.txt", 'r').readline())