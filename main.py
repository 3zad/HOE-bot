import nextcord
from cogs.general import GeneralCommands
from cogs.admin import AdminCommands
from cogs.moderation import ModerationCommands
from cogs.listeners import Listeners
from cogs.database_commands import DbCommands
from cogs.routines import Routines
from db.MainDatabase import MainDatabase
from config import Config

intents = nextcord.Intents.all()
intents.message_content = True
intents.reactions = True
intents.voice_states = True
intents.bans = True
intents.members = True

client = nextcord.ext.commands.Bot(command_prefix="owurghoerubheoruihoeb", intents=intents)


config = Config()
db = MainDatabase()

client.add_cog(GeneralCommands(client, config, db))
client.add_cog(Listeners(client, config, db))
client.add_cog(Routines(client, config, db))
client.add_cog(DbCommands(client, config, db))
client.add_cog(ModerationCommands(client, config, db))
client.add_cog(AdminCommands(client, config, db))


client.run(open("token.txt", 'r').readline().replace("\n", ""))