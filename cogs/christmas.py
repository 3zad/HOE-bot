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
    async def balance(self, ctx, member):
        user_data = await self.db.get_user_data(member[2:-1])
        if user_data:
            if ctx.user.id == member:
                await ctx.send(f"You have {user_data[1]} candy.")
            else:
                await ctx.send(f"{member} has {user_data[1]} candy.")
        else:
            await ctx.send("You don't have an account yet. Start earning candy first!")

    @nextcord.slash_command(name="work", description="Do some work and get some candy")
    async def work(self, ctx):
        amount = random.randint(1,25)
        await self.db.add_or_update_user(ctx.user.id, candy=amount)
        await self.db.update_last_work_time(ctx.user.id)
        await ctx.send(f"You worked and earned {amount} candy!")
        await ctx.response.send_message(f"You have earned {amount} pieces of candy!")
    
    @nextcord.slash_command(name="steal", description="Try stealing from a member.")
    async def steal(self, ctx, member):
        successful = random.choice([True, False])
        if successful:
            await ctx.response.send_message(f"You have stolen 50 pieces of candy from {member}!")
        else:
            await ctx.response.send_message(f"You failed and had to pay a fine of 200 candy to {member}!")

    @nextcord.slash_command(name="shield", description="Gives you a defense from stealing for 2 hours. Costs 25 candy.")
    async def shield(self, ctx, member):
        successful = random.choice([True, False])
        if successful:
            await ctx.response.send_message(f"You have stolen 50 pieces of candy from {member}!")
        else:
            await ctx.response.send_message(f"You failed and had to pay a fine of 200 candy to {member}!")

    @nextcord.slash_command(name="pay", description="Pay another user a specified amount.")
    async def pay(self, ctx, member, amount):
        amount = int(amount)
        funds = await self.sufficient_funds(ctx.user.id, amount)
        if amount < 1:
            await ctx.response.send_message(f"Please enter a whole number greater than or equal to 1!")
        if funds:
            await self.db.add_candy(ctx.user.id, -1*amount)
            await self.db.add_candy(member[2:-1], amount)
            await ctx.response.send_message(f"You have payed {amount} to {member}")
        else:    
            await ctx.response.send_message(f"Insufficient funds.")

    @nextcord.slash_command(name="ticket", description="Buy a lottery tickets (25 candy each).")
    async def ticket(self, ctx, tickets):
        tickets = int(tickets)
        if tickets < 1:
            await ctx.response.send_message(f"Please buy 1 or more tickets!")
        funds = await self.sufficient_funds(ctx.user.id, tickets*25)
        if funds:
            await self.db.add_to_lottery(ctx.user.id, tickets)
            await ctx.response.send_message(f"Successfully bought {tickets} ticket(s)!")
            
        else:
            await ctx.response.send_message(f"Insufficient funds.")

    @nextcord.slash_command(name="pot", description="Show how much money is in the lottery pot.")
    async def pot(self, ctx):
        pot = await self.db.get_lottery_pot()
        cont = await self.db.get_lottery_contributors()
        await ctx.response.send_message(pot)


    async def sufficient_funds(self, member, amount):
        data = await self.db.get_user_data(member)
        if data[1] > amount:
            return True
        return False