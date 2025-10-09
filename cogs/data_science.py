import nextcord
from nextcord.ext import commands
import re
from bot_utils.csv_utils import CSVUtils

class DataScience(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

        if config["mode"] == "production":
            self.commands_channel: list = self.config["commands_channel"]
        else:
            self.commands_channel: list = self.config["commands_channel_testing"]

    @nextcord.slash_command(name="science", description="Various data science commands.")
    async def science(self, ctx: nextcord.Interaction):
        if ctx.channel.id not in self.commands_channel:
            await ctx.response.send_message("Please go to bot command channel!", ephemeral=True)
            return

    @science.subcommand(name="lookup", description="Look up a word/user ID or set of words/user IDs")
    async def science_lookup(self, ctx: nextcord.Interaction, target):
        df = await CSVUtils.load_frequent_itemsets()

        word_mask = df['itemsets'].apply(lambda itemset: target in itemset)
        word_associations = df[word_mask].sort_values(by='support', ascending=False)

        embed=nextcord.Embed(
                title=f"Lookup for {target}",
                color=nextcord.colour.Colour.green()
            )

        pikkus = len(df)
        word_associations["count"] = (word_associations["support"] * pikkus).round(0).astype(int)

        embed.add_field(name="Ranking   Count   Support   Itemsets", value="", inline=False)

        results_list = []
        for i in range(0, min(len(word_associations),5)):
            global_rank = word_associations.index.values[i] + 1
            support_val = word_associations["support"].iloc[i]
            count_val = word_associations["count"].iloc[i]
            itemset_val = word_associations["itemsets"].iloc[i]

            itemset_string = ", ".join(list(itemset_val))
            itemset_display = itemset_string[:60] + "..." if len(itemset_string) > 60 else itemset_string

            result_line = (
                f"`{global_rank:<3}  {count_val:8}  {support_val:.4f}   {itemset_display}`"
            )
            results_list.append(result_line)

        if results_list == []:
            await ctx.response.send_message("No results.", ephemeral=True)
            return

        results_text = "\n".join(results_list)
        embed.add_field(name="\u200b", value=results_text, inline=False) 

        await ctx.send(embed=embed)


    @science.subcommand(name="ranking", description="Look up a ranking")
    async def science_ranking(self, ctx: nextcord.Interaction, ranking: int):
        df = await CSVUtils.load_frequent_itemsets()

        try:
            itemset = df["itemsets"].loc[ranking]
            await ctx.response.send_message(f"Ranking {ranking}: {", ".join(list(itemset))}")

        except KeyError:
            await ctx.response.send_message("Undefined index", ephemeral=True)