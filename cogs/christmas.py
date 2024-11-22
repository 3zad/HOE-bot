import nextcord
from nextcord.ext import commands
import random
from db.Database import Database

class ChristmasCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        print("HERE"*1000)
        await self.db.initialize()

    @nextcord.slash_command(name="balance", description="Check your balance.")
    async def balance(self, ctx):
        user_id = ctx.user.id
        user_data = await self.db.get_user_data(user_id)
        if user_data:
            await ctx.send(f"You have {user_data[1]} candy.")
        else:
            await ctx.send("You don't have an account yet. Start earning candy first!")

    @nextcord.slash_command(name="work", description="Do some work and get some candy")
    async def work(self, ctx):
        await self.db.add_or_update_user(ctx.user.id, candy=100)
        await self.db.update_last_work_time(ctx.user.id)
        await ctx.send("You worked and earned 100 candy!")
        await ctx.response.send_message("You have earned 5 pieces of candy!")
    
    @nextcord.slash_command(name="steal", description="Try stealing from a member.")
    async def steal(self, ctx, member):
        successful = bool(int(random.randint(0,199)/100))
        if successful:
            await ctx.response.send_message(f"You have stolen 50 pieces of candy from {member}!")
        else:
            await ctx.response.send_message(f"You failed and had to pay a fine of 200 candy to {member}!")