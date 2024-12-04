import nextcord
from nextcord.ext import commands, tasks
import random
from db.Database import Database
from datetime import datetime, timedelta
import asyncio

class ChristmasCommands(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.db = Database()
        self.config = config

        if config["mode"] == "production":
            self.work_channels = self.config["work_channel"]
            self.commands_channels =self.config["commands_channel"]
            self.approved_channels = self.config["approved_channels"]
        else:
            self.work_channels = self.config["work_channel_testing"]
            self.commands_channels =self.config["commands_channel_testing"]
            self.approved_channels = self.config["approved_channels_testing"]

        self.candy_gift_task.start()
        self.worker_task.start()

    async def embed(self, message, color, member, second_member=None):
        balance = await self.db.get_user_balance(member)
        stealing = await self.db.get_user_stealing(member)
        multiplier = await self.db.get_user_multiplier(member)
        gifts = await self.db.get_user_gifts(member)
        stolen_from = await self.db.get_user_stolen_from(member)
        workers = await self.db.get_user_workers(member)
        user = await self.bot.fetch_user(member)

        message = message.replace(f"<@{member}>", user.display_name)
        if second_member != None:
            second_user = await self.bot.fetch_user(second_member)
            message = message.replace(f"<@{second_member}>", second_user.display_name)

        description = f"<@{member}>'s balance: {balance} candy 🍬\nStealing attempts: {stealing}\nCandy multiplier: {multiplier}x\nNumber of gifts claimed: {gifts}\nThis user has been robbed {stolen_from} time(s).\nThis user has {workers} worker(s)."

        embed = nextcord.Embed(colour=color, color=None, title=message, type='rich', url=None, description=description, timestamp=None)
        try:
            user = await self.bot.fetch_user(member)
            embed.set_thumbnail(url=user.avatar)
        except:
            pass
        return embed

    @tasks.loop(minutes=60)  # Adjust the interval as needed
    async def candy_gift_task(self):
        """Periodically send a candy gift message to a random channel."""

        channel_id = random.choice(self.approved_channels)

        channel = self.bot.get_channel(channel_id)

        candy = random.randint(1000,5000)

        if channel:
            message = await channel.send(f"🎁 Happy Holidays! React quickly to claim {candy} candy! 🎁")
            await message.add_reaction("🍬")

            def check(reaction, user):
                return (
                    reaction.message.id == message.id
                    and str(reaction.emoji) == "🍬"
                    and not user.bot
                )

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0*60, check=check)
                await self.db.add_or_update_user(user.id, candy=candy, gifts=1)
                embed = await self.embed(f"🍬 {user.mention} claimed the candy! 🍬", nextcord.colour.Colour.green(), user.id)
                await channel.send(embed=embed)
            except asyncio.TimeoutError:
                await channel.send("😔 Nobody claimed the candy gift in time!")

    @tasks.loop(minutes=60)
    async def worker_task(self):
        users = await self.db.get_users_with_workers()
        if users == []:
            return
        for user in users:
            member_id = int(user[0])
            worker_count = int(user[1])
            multiplier = await self.db.get_user_multiplier(member_id)
            await self.db.add_or_update_user(member_id, candy=worker_count*100*multiplier)
            

    @candy_gift_task.before_loop
    async def before_candy_gift_task(self):
        await self.bot.wait_until_ready()
        await self.db.initialize()

    @worker_task.before_loop
    async def before_worker_task(self):
        await self.bot.wait_until_ready()
        await self.db.initialize()


    @nextcord.slash_command(name="upgrade", description="Increment your multiplier by 1! Costs 1000 candy plus 2000 times your current candy multiplier.")
    async def upgrade(self, ctx):
        color = None
        message = ""
        if ctx.channel.id in self.commands_channels:
            multiplier = await self.db.get_user_multiplier(ctx.user.id)
            damage = 1000+int(multiplier)*2000
            funds = await self.sufficient_funds(ctx.user.id, damage)

            if int(multiplier) >= 10:
                message = f"You have the maximum multipler. You cannot upgrade further."
                color = nextcord.colour.Colour.red()
            elif funds:
                await self.db.add_or_update_user(ctx.user.id, candy=-damage)
                await self.db.add_or_update_user(ctx.user.id, multiplier=1.0)
                message = f"Multiplier upgraded!"
                color = nextcord.colour.Colour.green()
            else:
                message = f"Insufficient funds. You need {str(damage)} candy!"
                color = nextcord.colour.Colour.red()

            embed = await self.embed(message, color, ctx.user.id)
            await ctx.response.send_message(embed=embed)


    @nextcord.slash_command(name="balance", description="Check your balance.")
    async def balance(self, ctx, member):
        color = None
        message = ""
        if ctx.channel.id in self.commands_channels:
            user_data = await self.db.get_user_data(member[2:-1])
            member_id = int(member[2:-1])
            if user_data:
                if ctx.user.id == member_id:
                    message = f"You have {user_data[1]} candy."
                    color = nextcord.colour.Colour.blue()
                else:
                    message = f"{member} has {user_data[1]} candy."
                    color = nextcord.colour.Colour.blue()
            else:
                if ctx.user.id == member_id:
                    message = "You don't have an account yet. Start earning candy first!"
                    color = nextcord.colour.Colour.red()
                else:
                    message = f"{member} doesn't have an account yet."
                    color = nextcord.colour.Colour.red()

            embed = await self.embed(message, color, member_id)
            await ctx.response.send_message(embed=embed)


    @nextcord.slash_command(name="work", description="Do some work and get some candy")
    async def work(self, ctx):
        color = None
        message = ""
        if ctx.channel.id in self.work_channels:
            info = await self.db.get_user_data(ctx.user.id)
            rare_gem = random.randint(0, 100) == 20

            work = True
            if info != None and info[2] is not None:
                last_work = datetime.fromisoformat(info[2])
                time_since_last = datetime.now() - last_work

                if time_since_last < timedelta(minutes=5):
                    minutes_remaining = 5 - time_since_last.total_seconds() // 60
                    message = f"You can work again in {int(minutes_remaining)} minute(s)!"
                    color = nextcord.colour.Colour.red()
                    work = False
            if work:
                multiplier = await self.db.get_user_multiplier(ctx.user.id)
                await self.db.update_last_work_time(ctx.user.id)
                candy = random.randint(50,100) * int(multiplier)
                if rare_gem:
                    candy = (candy + 20) * 20
                    await self.db.add_or_update_user(ctx.user.id, candy=candy, work_count=1)
                    message = f"🍬 You found a rare gem and earned {candy} candy! 🍬"
                    color = nextcord.colour.Colour.green()
                else:
                    await self.db.add_or_update_user(ctx.user.id, candy=candy, work_count=1)
                    message = f"🍬 You mined for gems and earned {candy} candy! 🍬"
                    color = nextcord.colour.Colour.green()

            embed = await self.embed(message, color, ctx.user.id)
            await ctx.response.send_message(embed=embed)

    
    @nextcord.slash_command(name="steal", description="Try stealing from a member.")
    async def steal(self, ctx, member, amount):
        if ctx.channel.id in self.commands_channels:

            color = None
            message = ""
            amount = int(amount)
            
            if amount < 1:
                message = f"Please enter a whole number greater than or equal to 1!"
                color = nextcord.colour.Colour.red()
            else:
                shielded = True
                victim_shield, victim_hours = None, None
                victim_funds = None
                try:
                    victim_shield, victim_hours = await self.db.get_user_shield_date(member[2:-1])
                    victim_funds = await self.sufficient_funds(member[2:-1], amount*10)
                except TypeError:
                    shielded = False

                robber_funds = await self.sufficient_funds(ctx.user.id, 0)

                
                if shielded and victim_shield != None:
                    last_shield = datetime.fromisoformat(victim_shield)
                    time_since_last_shield = datetime.now() - last_shield
                else:
                    shielded = False

                if ctx.user.id == int(member[2:-1]):
                    message = f"You can't steal from yourself!"
                    color = nextcord.colour.Colour.red()
                elif not robber_funds:
                    message = f"You're too poor!"
                    color = nextcord.colour.Colour.red()
                elif shielded and time_since_last_shield < timedelta(hours=victim_hours):
                    message = f"{member} is shielded!"
                    color = nextcord.colour.Colour.red()
                elif victim_funds:
                    await self.db.update_last_shield_time(member[2:-1], 0)
                    stealing_attempts = await self.db.get_user_stealing(ctx.user.id)
                    successful = random.random() < (1.001**(-amount) - float(stealing_attempts)/100)

                    await self.db.increment_stealing_attempts(ctx.user.id)

                    if successful:
                        await self.db.add_or_update_user(ctx.user.id, candy=amount)
                        await self.db.add_or_update_user(member[2:-1], candy=-amount)
                        await self.db.increment_stolen_from(member[2:-1])
                        message = f"🍬 You have stolen {amount} pieces of candy from {member}! 🍬"
                        color = nextcord.colour.Colour.green()
                    else:
                        await self.db.add_or_update_user(ctx.user.id, candy=-amount*2)
                        await self.db.add_or_update_user(member[2:-1], candy=amount)
                        message = f"You failed and had to pay a fine of {amount*2} pieces of candy to {member}!"
                        color = nextcord.colour.Colour.red()
                
                else:
                    message = f"{member} is too poor!"
                    color = nextcord.colour.Colour.red()

            embed = await self.embed(message, color, ctx.user.id, second_member=member[2:-1])
            await ctx.response.send_message(embed=embed)


    @nextcord.slash_command(name="pardon", description="Clear your stealing attempts for 1000 candy.")
    async def pardon(self, ctx):
        color = None
        message = ""

        if ctx.channel.id in self.commands_channels:
            funds = await self.sufficient_funds(ctx.user.id, 1000)

            if funds:
                await self.db.add_or_update_user(ctx.user.id, candy=-1000)
                await self.db.clear_stealing_attempts(ctx.user.id)
                message = f"Stealing attempts cleared."
                color = nextcord.colour.Colour.green()
            else:
                message = "Insufficient funds. Maybe try stealing?"
                color = nextcord.colour.Colour.red()

            embed = await self.embed(message, color, ctx.user.id)
            await ctx.response.send_message(embed=embed)

    @nextcord.slash_command(name="shield", description="Gives you a defense from stealing for 2 hours. It costs 150 candy per hour.")
    async def shield(self, ctx, hours):
        color = None
        message = ""
        if ctx.channel.id in self.commands_channels:
            hours = int(hours)
            if hours >= 1:
                funds = await self.sufficient_funds(ctx.user.id, hours*150)
                
                if funds:
                    shield, hours_db = await self.db.get_user_shield_date(ctx.user.id)
                    if shield != None and int(hours_db) > 0:
                        last_shield = datetime.fromisoformat(shield)
                        time_since_last_shield = datetime.now() - last_shield

                        if time_since_last_shield < timedelta(hours=hours_db):
                            hours = hours + int(hours_db) - round(time_since_last_shield.total_seconds()/3600, 0)

                    await self.db.update_last_shield_time(ctx.user.id, hours)
                    await self.db.add_or_update_user(ctx.user.id, candy=hours*150*-1)
                    message = f"You have been shielded against robbers for {hours} hour(s)!"
                    color = nextcord.colour.Colour.green()
                else:
                    message = f"Insufficient funds."
                    color = nextcord.colour.Colour.red()
            else:
                message = f"Please enter a valid number."
                color = nextcord.colour.Colour.red()

            embed = await self.embed(message, color, ctx.user.id)
            await ctx.response.send_message(embed=embed)            
            

    @nextcord.slash_command(name="pay", description="Pay another user a specified amount.")
    async def pay(self, ctx, member, amount):
        color = None
        message = ""

        if ctx.channel.id in self.commands_channels:
            amount = int(amount)
            funds = await self.sufficient_funds(ctx.user.id, amount)

            if amount < 1:
                message = f"Please enter a whole number greater than or equal to 1!"
                color = nextcord.colour.Colour.red()
            else:
                if funds:
                    await self.db.add_or_update_user(ctx.user.id, candy=-1*amount)
                    await self.db.add_or_update_user(member[2:-1], candy=amount)
                    message = f"You have payed {amount} to {member}"
                    color = nextcord.colour.Colour.green()
                else:    
                    message = f"Insufficient funds."
                    color = nextcord.colour.Colour.red()

            embed = await self.embed(message, color, ctx.user.id, second_member=member[2:-1])
            await ctx.response.send_message(embed=embed)    

    @nextcord.slash_command(name="ticket", description="Buy a lottery tickets (25 candy each).")
    async def ticket(self, ctx, tickets):
        color = None
        message = ""
        if ctx.channel.id in self.commands_channels:
            tickets = int(tickets)
            if tickets < 1:
                message = f"Please buy 1 or more tickets!"
                color = nextcord.colour.Colour.red()
            else:
                funds = await self.sufficient_funds(ctx.user.id, tickets*25)
                if funds:
                    await self.db.add_to_lottery(ctx.user.id, tickets)
                    message = f"Successfully bought {tickets} ticket(s)!"
                    color = nextcord.colour.Colour.green()
                    
                else:
                    message = f"Insufficient funds."
                    color = nextcord.colour.Colour.red()

            embed = await self.embed(message, color, ctx.user.id)
            await ctx.response.send_message(embed=embed)    

    @nextcord.slash_command(name="pot", description="Show how much money is in the lottery pot.")
    async def pot(self, ctx):
        if ctx.channel.id in self.commands_channels:
            pot = await self.db.get_lottery_pot()
            tickets = await self.db.get_user_tickets(ctx.user.id)
            embed = nextcord.Embed(colour=nextcord.colour.Colour.blue(), color=None, title=f"Money in the lottery pot: {str(pot)}", type='rich', url=None, description=f"You have {tickets} tickets.", timestamp=None)
            await ctx.response.send_message(embed=embed) 

    @nextcord.slash_command(name="daily", description="Claim your daily reward!")
    async def daily(self, ctx):
        color = None
        message = ""
        if ctx.channel.id in self.commands_channels:
            info = await self.db.get_user_data(ctx.user.id)
            daily = True
            if info[6] is not None:
                last_daily = datetime.fromisoformat(info[6])
                time_since_last = datetime.now() - last_daily

                if time_since_last < timedelta(hours=20):  # Check if less than 20 hours
                    hours_remaining = 20 - time_since_last.total_seconds() // 3600
                    message = f"You can claim your daily reward in {int(hours_remaining)} hours!"
                    color = nextcord.colour.Colour.red()
                    daily = False

            if daily:
                await self.db.update_last_daily_time(ctx.user.id)
                multiplier = await self.db.get_user_multiplier(ctx.user.id)
                candy = random.randint(500, 1500) * int(multiplier)
                await self.db.add_or_update_user(ctx.user.id, candy=candy)
                message = f"You've earned {candy} candy!"
                color = nextcord.colour.Colour.green()

            embed = await self.embed(message, color, ctx.user.id)
            await ctx.response.send_message(embed=embed)

        
    @nextcord.slash_command(name="coinflip", description="50/50 chance of doubling your money or losing it. 5% tax.")
    async def coinflip(self, ctx, amount):
        color = None
        message = ""
        if ctx.channel.id in self.commands_channels:
            amount = int(amount)
            if amount < 1:
                message = f"Please enter a whole number greater than or equal to 1!"
                color = nextcord.colour.Colour.red()

            else:
                funds = await self.sufficient_funds(ctx.user.id, amount)

                user_won = random.choice([True,False])

                if funds:
                    if user_won:
                        await self.db.add_or_update_user(ctx.user.id, candy=amount, gambling_count=1)
                        message = f"You won {amount} candy!"
                        color = nextcord.colour.Colour.green()
                    else:
                        await self.db.add_or_update_user(ctx.user.id, candy=amount*-1, gambling_count=1)
                        message = f"You lost {amount} candy!"
                        color = nextcord.colour.Colour.red()
                else:
                    message = "Insufficient funds."
                    color = nextcord.colour.Colour.red()

            embed = await self.embed(message, color, ctx.user.id)
            await ctx.response.send_message(embed=embed)  


    @nextcord.slash_command(name="buy_worker", description="Buy a worker for 1000 candy. The worker will make you 100 candy * your multiplier per hour.")
    async def buy_worker(self, ctx, number):
        color = None
        message = ""
        if ctx.channel.id in self.commands_channels:
            number = int(number)
            worker_count = await self.db.get_user_workers(ctx.user.id)
            if number < 1:
                message = "Please enter an integer equal or above 1."
                color = nextcord.colour.Colour.red()
            elif int(worker_count + number) >= 100:
                message = "You have reached the maximum number of workers or you are trying to buy too many workers (maximum 100 workers)!"
                color = nextcord.colour.Colour.red()
            else:
                funds = await self.sufficient_funds(ctx.user.id, number*1000)

                if funds:
                    await self.db.add_or_update_user(ctx.user.id, candy=-number*1000, worker_count=number)
                    message = f"Successfully bought {str(number)} workers!"
                    color = nextcord.colour.Colour.green()
                else:
                    message = "Insufficient funds."
                    color = nextcord.colour.Colour.red()

            embed = await self.embed(message, color, ctx.user.id)
            await ctx.response.send_message(embed=embed)  


    async def sufficient_funds(self, member, amount):
        data = await self.db.get_user_data(member)
        if int(data[1]) > int(amount):
            return True
        return False