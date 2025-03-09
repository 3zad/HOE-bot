import nextcord
from nextcord.ext import commands
import sys
from db.ChristmasDatabase import Database
from db.MainDatabase import MainDatabase

class AdminCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = Database()
        self.main_db = MainDatabase()
        
        self.config = config
        self.admins = config["owners"]

    @nextcord.slash_command(name="shutdown", description="(Admin command) Turn off the bot")
    async def shutdown(self, ctx):
        if ctx.user.id in self.admins:
            await ctx.send("Shutting down!")
            sys.exit(0)

    @nextcord.slash_command(name="manual_db_start", description="(Admin command) Start the database if discord is being weird.")
    async def manual_db_start(self, ctx):
        if ctx.user.id in self.admins:
            await self.main_db.initialize()
            await ctx.send("Started.")
    
    @nextcord.slash_command(name="sync_commands", description="(Admin command) Sync commands.")
    async def sync_commands(self, ctx):
        if ctx.user.id in self.admins:
            await self.bot.sync_application_commands()
            await ctx.send(f"Done.")

    @nextcord.slash_command(name="draw_lottery", description="(Admin command) Draw the lottery.")
    async def draw_lottery(self, ctx):
        if ctx.user.id in self.admins:
            winner_id, winnings = await self.db.draw_lottery()
            await ctx.send(f"🍬🍬🍬 <@{winner_id}> has won {winnings} candy! 🍬🍬🍬")

    @nextcord.slash_command(name="candy_injection", description="(Admin command) Candy injection.")
    async def candy_injection(self, ctx, amount):
        if ctx.user.id in self.admins:
            await self.db.add_or_update_user(ctx.user.id, candy=amount)
            await ctx.send(f"Injection {amount} candy.")

    @nextcord.slash_command(name="backup", description="(Admin command) Backup the database")
    async def backup(self, ctx):
        if ctx.user.id in self.admins:
            channel = self.bot.get_channel(1312055600062005298)
            await channel.send(file=nextcord.File('main.db'))
            await ctx.send("Done.")

    @nextcord.slash_command(name="info", description="(Admin command) Database info of a user.")
    async def info(self, ctx, member):
        if ctx.user.id in self.admins:
            user = await self.db.get_user_data(member[2:-1])
            if user == None:
                user = f"{member[2:-1]} not in DB!"
            await ctx.send(user)

    @nextcord.slash_command(name="reset", description="(Admin command) Resets everyone's balance to 1000 times their multiplier.")
    async def reset(self, ctx):
        if ctx.user.id in self.admins:
            await self.db.reset_balances()
            await ctx.send("Done.")

    @nextcord.slash_command(name="drop_reactions", description="(Admin command) Drop the reactions table.")
    async def drop_reactions(self, ctx):
        if ctx.user.id == 740986064314826822:
            await self.main_db.drop_reaction_table()
            await ctx.send("Done.")

    @nextcord.slash_command(name="drop_starred", description="(Admin command) Drop the starred table.")
    async def drop_starred(self, ctx):
        if ctx.user.id == 740986064314826822:
            await self.main_db.drop_starred_table()
            await ctx.send("Done.")


    # --- Not in use --- #
    @nextcord.slash_command(name="christmas_backup", description="(Admin command) Backup the christmas database")
    async def backup(self, ctx):
        if ctx.user.id in self.admins:
            channel = self.bot.get_channel(1312055600062005298)
            await channel.send(file=nextcord.File('economy.db'))
            await ctx.send("Done.")