import nextcord
from nextcord.ext import commands
import sys
from db.ChristmasDatabase import Database

class ChristmasAdminCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = Database()
        
        self.config = config
        self.admins = config["owners"]

    @nextcord.slash_command(name="shutdown", description="(Admin command) Turn off the bot")
    async def shutdown(self, ctx):
        if ctx.user.id in self.admins:
            await ctx.send("Shutting down!")
            sys.exit(0)

    # --- Not in use --- #
    @nextcord.slash_command(name="christmas_backup", description="(Admin command) Backup the christmas database")
    async def backup(self, ctx):
        if ctx.user.id in self.admins:
            channel = self.bot.get_channel(1312055600062005298)
            await channel.send(file=nextcord.File('economy.db'))
            await ctx.send("Done.")

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