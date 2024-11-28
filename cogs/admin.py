import nextcord
from nextcord.ext import commands
import sys
from db.Database import Database

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.has_permissions(administrator = True)
    @nextcord.slash_command(name="shutdown", description="Turn off the bot")
    async def hello(self, ctx):
        sys.exit(0)

    @commands.has_permissions(administrator = True)
    @nextcord.slash_command(name="manual_db_start", description="Start the database if discord is being weird.")
    async def manual_db_start(self, ctx):
        await self.db.initialize()
        await ctx.send("Started.")
    
    @commands.has_permissions(administrator = True)
    @nextcord.slash_command(name="draw_lottery", description="Draw the lottery.")
    async def draw_lottery(self, ctx):
        winner_id, winnings = await self.db.draw_lottery()
        await ctx.send(f"<@{winner_id}> has won {winnings} candy!")


    @commands.has_permissions(administrator = True)
    @nextcord.slash_command(name="candy_injection", description="Candy injection.")
    async def candy_injection(self, ctx, amount):
        await self.db.add_candy(ctx.user.id, amount)
        await ctx.send(f"Injection {amount} candy.")
        
    @commands.has_permissions(administrator = True)
    @nextcord.slash_command(name="candy_injection_bank", description="Candy injection for the bank.")
    async def candy_injection_bank(self, ctx, amount):
        await self.db.add_candy_bank(amount)
        await ctx.send(f"Injection {amount} candy into the bank.")