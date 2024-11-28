import nextcord
from nextcord.ext import commands
import random
from db.Database import Database
from datetime import datetime, timedelta

class ChristmasCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        print("HERE"*1000)
        await self.db.initialize()

    @nextcord.slash_command(name="bank_balance", description="See how much money the bank has.")
    async def bank_balance(self, ctx):
        info = await self.db.get_bank_data()
        print(info)
        await ctx.response.send_message(info[1])


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
        info = await self.db.get_user_data(ctx.user.id)

        rare_gem = random.randint(0, 100) == 99

        if info != None and info[2] is not None:
            last_work = datetime.fromisoformat(info[2])
            time_since_last = datetime.now() - last_work

            if time_since_last < timedelta(minutes=5):  # Check if less than 20 hours
                minutes_remaining = 5 - time_since_last.total_seconds() // 60
                await ctx.response.send_message(f"You can work again in {int(minutes_remaining)} minutes!")
                return
        await self.db.update_last_work_time(ctx.user.id)
        candy = random.randint(1,25)
        if rare_gem:
            candy = (candy + 20) * 20
            await self.db.add_candy(ctx.user.id, candy)
            await ctx.response.send_message(f"You found a rare gem and earned {candy} candy!")
        else:
            await self.db.add_candy(ctx.user.id, candy)
            await ctx.response.send_message(f"You mined for gems and earned {candy} candy!")
        await self.db.add_candy_bank(-1*candy)
    
    
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

    @nextcord.slash_command(name="daily", description="Claim your daily reward!")
    async def daily(self, ctx):
        info = await self.db.get_user_data(ctx.user.id)

        if info[6] is not None:
            last_daily = datetime.fromisoformat(info[6])
            time_since_last = datetime.now() - last_daily

            if time_since_last < timedelta(hours=20):  # Check if less than 20 hours
                hours_remaining = 20 - time_since_last.total_seconds() // 3600
                await ctx.response.send_message(f"You can claim your daily reward in {int(hours_remaining)} hours!")
                return
        await self.db.update_last_daily_time(ctx.user.id)
        candy = random.randint(500, 1500)
        await self.db.add_candy(ctx.user.id, candy)
        await ctx.response.send_message(f"You've earned {candy} candy!")
        await self.db.add_candy_bank(-1*candy)
        
    @nextcord.slash_command(name="coinflip", description="50/50 chance of doubling your money or losing it.")
    async def coinflip(self, ctx, amount):
        funds = await self.sufficient_funds(ctx.user.id, amount)

        user_won = random.choice([True,False])
        print(user_won)

        if funds:
            if user_won:
                await self.db.add_candy(ctx.user.id, amount)
                await self.db.add_candy_bank(-1*amount)
                await ctx.response.send_message(f"You won {amount} candy!")
            else:
                await self.db.add_candy(ctx.user.id, -1*amount)
                await self.db.add_candy_bank(amount)
                await ctx.response.send_message(f"You lost {amount} candy!")
        else:
            await ctx.response.send_message("Insufficient funds.")

    async def sufficient_funds(self, member, amount):
        data = await self.db.get_user_data(member)
        if int(data[1]) > int(amount):
            return True
        return False