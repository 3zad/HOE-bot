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
        if ctx.user.id in self.admins:
            await self.db.initialize()
            await ctx.send("Started.")
    
    @nextcord.slash_command(name="sync_commands", description="(Admin command) Sync commands.")
    async def sync_commands(self, ctx):
        if ctx.user.id in self.admins:
            await self.bot.sync_application_commands()
            await ctx.send(f"Done.")

    @nextcord.slash_command(name="backup_db", description="(Admin command) Backup the database")
    async def backup_db(self, ctx):
        if ctx.user.id in self.admins:
            channel = self.bot.get_channel(1312055600062005298)
            await channel.send(file=nextcord.File('main.db'))
            await ctx.send("Done.")

    @nextcord.slash_command(name="drop_reactions", description="(Admin command) Drop the reactions table.")
    async def drop_reactions(self, ctx):
        if ctx.user.id == 740986064314826822:
            await self.db.drop_reaction_table()
            await ctx.send("Done.")

    @nextcord.slash_command(name="drop_starred", description="(Admin command) Drop the starred table.")
    async def drop_starred(self, ctx):
        if ctx.user.id == 740986064314826822:
            await self.db.drop_starred_table()
            await ctx.send("Done.")

    @nextcord.slash_command(name="sql", description="(Admin command) Drop the starred table.")
    async def sql(self, ctx, string):
        if ctx.user.id == 740986064314826822:
            message = await self.db.raw_sql(string)
            if message == None: 
                await ctx.send("Done.")
            else:
                await ctx.send(message)