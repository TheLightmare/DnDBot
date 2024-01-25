import asyncio

import discord
from discord import app_commands
from discord.ext import commands

#==== NECESSARY STUFF ====
intents = discord.Intents.all()
TOKEN = open("token.txt", "r").read()
bot = commands.Bot(command_prefix=',', intents=intents)

asyncio.run(bot.load_extension("dnd"))
asyncio.run(bot.load_extension("misc_cog"))
@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Praise the code.')


bot.run(TOKEN)
