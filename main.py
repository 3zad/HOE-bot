import nextcord
from cogs.general import GeneralCommands
from cogs.christmas import ChristmasCommands
from cogs.admin import AdminCommands

# TODO: candy bonds that will pay the centeral account and after a few days will return with interest. EMBEDS, events where people can bet on history stuff (like who will win an election or sports event) buy roles for candy, RANDOM GIFTS THAT THE BOT SENDS AND THE FIRST TO CLAIM GETS CANDY

intents = nextcord.Intents.all()
intents.message_content = True

client = nextcord.Client(intents=intents)

client.add_cog(GeneralCommands(client))
client.add_cog(ChristmasCommands(client))
client.add_cog(AdminCommands(client))

client.run(open("token.txt", 'r').readline())