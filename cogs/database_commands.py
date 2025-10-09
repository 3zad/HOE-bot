import nextcord
from nextcord.ext import commands
from db.MainDatabase import MainDatabase

class DbCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = MainDatabase()
        
        self.config = config
        self.admins = config["owners"]

    @nextcord.slash_command(name="manual_db_start", description="(Admin command) Start the database if discord is being weird.")
    async def manual_db_start(self, ctx):
        if ctx.user.id in self.admins or ctx.user.id == 843958503324123144:
            await self.db.initialize()
            await ctx.send("Started.")

    @nextcord.slash_command(name="backup_db", description="(Admin command) Backup the database")
    async def backup_db(self, ctx):
        if ctx.user.id in self.admins:
            channel = self.bot.get_channel(1312055600062005298)
            await channel.send(file=nextcord.File('main.db'))
            await ctx.send("Done.")

    @nextcord.slash_command(name="sql", description="(Bot dev command) Execute sql.")
    async def sql(self, ctx, string):
        if ctx.user.id == 740986064314826822:
            message = await self.db.raw_sql(string)
            if message == None: 
                await ctx.send("Done.")
            else:
                await ctx.send(message)