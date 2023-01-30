import discord
from discord.ext import commands

class Dnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog loaded successfully')

    @commands.command()
    async def test(self, ctx):
        await ctx.send("Test")

async def setup(bot):
    await bot.add_cog(Dnd(bot))