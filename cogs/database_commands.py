import nextcord
from nextcord.ext import commands
from cogs.__checks import dev_only

class DbCommands(commands.Cog):
    def __init__(self, bot, config, db):
        self.bot = bot
        self.db = db
        self.config = config

    @nextcord.slash_command(name="manual_db_start", description="(Admin command) Start the database if discord is being weird.")
    @dev_only()
    async def manual_db_start(self, ctx):
        await self.db.initialize()
        await ctx.send("Started.")

    @nextcord.slash_command(name="backup_db", description="(Admin command) Backup the database")
    @dev_only()
    async def backup_db(self, ctx):
        # Hardcoded channel id in the HOE discord
        channel = self.bot.get_channel(1312055600062005298)
        await channel.send(file=nextcord.File('main.db'))
        await ctx.send("Done.")

    @nextcord.slash_command(name="sql", description="(Bot dev command) Execute sql.")
    @dev_only()
    async def sql(self, ctx, string):
        message = await self.db.raw_sql(string)
        if message == None: 
            await ctx.send("Done.")
        else:
            await ctx.send(message)

    @nextcord.slash_command(name="migrate", description="(Bot dev command) Migrate the database.")
    @dev_only()
    async def migrate(self, ctx):
        await self.db.migrate()
        await ctx.send("Migration complete.")