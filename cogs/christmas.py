import nextcord
from nextcord.ext import commands
import random
from db.Database import Database
from datetime import datetime, timedelta

class ChristmasCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = Database()
        self.config = config

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        await self.db.initialize()

    @nextcord.slash_command(name="balance", description="Check your balance.")
    async def balance(self, ctx, member):
        color = None
        message = ""
        if ctx.channel.id in self.config["commands_channel"]:
            user_data = await self.db.get_user_data(member[2:-1])
            if user_data:
                if ctx.user.id == member:
                    message = f"You have {user_data[1]} candy."
                    color = nextcord.colour.Colour.green()
                else:
                    message = f"{member} has {user_data[1]} candy."
                    color = nextcord.colour.Colour.green()
            else:
                if ctx.user.id == member[2:-1]:
                    message = "You don't have an account yet. Start earning candy first!"
                    color = nextcord.colour.Colour.red()
                else:
                    message = f"{member} doesn't have an account yet."
                    color = nextcord.colour.Colour.red()
        
        embed = nextcord.Embed(colour=color, color=None, title=None, type='rich', url=None, description=message, timestamp=None)
        try:
            user = await self.bot.fetch_user(member[2:-1])
            embed.set_thumbnail(url=user.avatar)
        except:
            pass
        await ctx.response.send_message(embed=embed)

    @nextcord.slash_command(name="work", description="Do some work and get some candy")
    async def work(self, ctx):
        color = None
        message = ""
        if ctx.channel.id in self.config["work_channel"]:
            info = await self.db.get_user_data(ctx.user.id)

            rare_gem = random.randint(0, 100) == 99

            work = True
            if info != None and info[2] is not None:
                last_work = datetime.fromisoformat(info[2])
                time_since_last = datetime.now() - last_work

                if time_since_last < timedelta(minutes=5):  # Check if less than 20 hours
                    minutes_remaining = 5 - time_since_last.total_seconds() // 60
                    message = f"You can work again in {int(minutes_remaining)} minutes!"
                    color = nextcord.colour.Colour.red()
                    work = False
            if work:
                await self.db.update_last_work_time(ctx.user.id)
                candy = random.randint(1,25)
                if rare_gem:
                    candy = (candy + 20) * 20
                    await self.db.add_or_update_user(ctx.user.id, candy=candy)
                    message = f"🍬 You found a rare gem and earned {candy} candy! 🍬"
                    color = nextcord.colour.Colour.green()
                else:
                    await self.db.add_or_update_user(ctx.user.id, candy=candy)
                    message = f"🍬 You mined for gems and earned {candy} candy! 🍬"
                    color = nextcord.colour.Colour.green()
        else:
            print(self.config["work_channel"], ctx.channel.id)

        balance = await self.db.get_user_balance(ctx.user.id)
        embed = nextcord.Embed(colour=color, color=None, title=message, type='rich', url=None, description=f"Member balance: {balance} candy 🍬", timestamp=None)
        try:
            user = await self.bot.fetch_user(ctx.user.id)
            embed.set_thumbnail(url=user.avatar)
        except:
            pass
        await ctx.response.send_message(embed=embed)

    
    @nextcord.slash_command(name="steal", description="Try stealing from a member. Each stealing attempt worsens your chances at successfully stealing by 1%. After 100 stealing attempts there will be a 0% chance of you being successful with any amount of money. The less you steal the less likely you are to get caught...")
    async def steal(self, ctx, member, amount):
        if ctx.channel.id in self.config["commands_channel"]:
            amount = int(amount)
            
            victim_funds = await self.sufficient_funds(member[2:-1], amount*10)

            info = await self.db.get_user_data(ctx.user.id)

            robber_funds = await self.sufficient_funds(ctx.user.id, 2*(int(info[2])+500))

            if not robber_funds:
                message = f"You're too poor!"
            elif victim_funds:
                info = await self.db.get_user_data(ctx.user.id)
                successful = random.random() < (1.001**(-amount) - float(info[3])/100)

                await self.db.increment_stealing_attempts(ctx.user.id)

                if successful:
                    await self.db.add_or_update_user(ctx.user.id, candy=amount)
                    await self.db.add_or_update_user(member[2:-1], candy=-amount)
                    message = f"You have stolen {amount} pieces of candy from {member}!"
                else:
                    await self.db.add_or_update_user(ctx.user.id, candy=-amount*2)
                    await self.db.add_or_update_user(member[2:-1], candy=amount)
                    message = f"You failed and had to pay a fine of {amount*2} pieces of candy to {member}!"
            
            else:
                message = f"{member} is too poor!"

    @nextcord.slash_command(name="pardon", description="Clear your stealing attempts for 1000 candy.")
    async def pardon(self, ctx):
        if ctx.channel.id in self.config["commands_channel"]:
            funds = await self.sufficient_funds(ctx.user.id, 1000)

            if funds:
                self.db.add_or_update_user(ctx.user.id, candy=-1000)
                self.db.clear_stealing_attempts(ctx.user.id)
                message = f"Stealing attempts cleared."
            else:
                message = "Insufficient funds. Maybe try stealing?"

    @nextcord.slash_command(name="shield", description="Gives you a defense from stealing for 2 hours. It costs 50 candy per hour.")
    async def shield(self, ctx, hours):
        if ctx.channel.id in self.config["commands_channel"]:
            hours = int(hours)
            if hours >= 1:
                funds = await self.sufficient_funds(ctx.user.id, hours*50)
                
                if funds:
                    await self.db.update_last_shield_time(ctx.user.id, hours)
                    await self.db.add_or_update_user(ctx.user.id, candy=hours*50*-1)
                    message = f"You have been shielded against robbers for {hours} hour(s)!"
                else:
                    message = f"Insufficient funds."
            else:
                ctx.response.send_message(f"Please enter a valid number.")

    @nextcord.slash_command(name="pay", description="Pay another user a specified amount.")
    async def pay(self, ctx, member, amount):
        if ctx.channel.id in self.config["commands_channel"]:
            amount = int(amount)
            funds = await self.sufficient_funds(ctx.user.id, amount)
            if amount < 1:
                message = f"Please enter a whole number greater than or equal to 1!"
            if funds:
                await self.db.add_or_update_user(ctx.user.id, candy=-1*amount)
                await self.db.add_or_update_user(member[2:-1], candy=amount)
                message = f"You have payed {amount} to {member}"
            else:    
                message = f"Insufficient funds."

    @nextcord.slash_command(name="ticket", description="Buy a lottery tickets (25 candy each).")
    async def ticket(self, ctx, tickets):
        if ctx.channel.id in self.config["commands_channel"]:
            tickets = int(tickets)
            if tickets < 1:
                message = f"Please buy 1 or more tickets!"
            funds = await self.sufficient_funds(ctx.user.id, tickets*25)
            if funds:
                await self.db.add_to_lottery(ctx.user.id, tickets)
                message = f"Successfully bought {tickets} ticket(s)!"
                
            else:
                message = f"Insufficient funds."

    @nextcord.slash_command(name="pot", description="Show how much money is in the lottery pot.")
    async def pot(self, ctx):
        if ctx.channel.id in self.config["commands_channel"]:
            pot = await self.db.get_lottery_pot()
            message = pot

    @nextcord.slash_command(name="daily", description="Claim your daily reward!")
    async def daily(self, ctx):
        if ctx.channel.id in self.config["commands_channel"]:
            info = await self.db.get_user_data(ctx.user.id)

            if info[6] is not None:
                last_daily = datetime.fromisoformat(info[6])
                time_since_last = datetime.now() - last_daily

                if time_since_last < timedelta(hours=20):  # Check if less than 20 hours
                    hours_remaining = 20 - time_since_last.total_seconds() // 3600
                    message = f"You can claim your daily reward in {int(hours_remaining)} hours!"
                    return
            await self.db.update_last_daily_time(ctx.user.id)
            candy = random.randint(500, 1500)
            await self.db.add_or_update_user(ctx.user.id, candy=candy)
            message = f"You've earned {candy} candy!"
        
    @nextcord.slash_command(name="coinflip", description="50/50 chance of doubling your money or losing it. 5% tax.")
    async def coinflip(self, ctx, amount):
        if ctx.channel.id in self.config["commands_channel"]:
            amount = int(amount)
            funds = await self.sufficient_funds(ctx.user.id, amount)

            user_won = random.choice([True,False])

            if funds:
                if user_won:
                    await self.db.add_or_update_user(ctx.user.id, candy=amount)
                    message = f"You won {amount} candy!"
                else:
                    await self.db.add_or_update_user(ctx.user.id, candy=amount*-1)
                    message = f"You lost {amount} candy!"
            else:
                message = "Insufficient funds."

    async def sufficient_funds(self, member, amount):
        data = await self.db.get_user_data(member)
        if int(data[1]) > int(amount):
            return True
        return False