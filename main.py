import asyncio

import discord
from discord import app_commands
from discord.ext import commands

#==== NECESSARY STUFF ====
intents = discord.Intents.all()
TOKEN = ""
bot = commands.Bot(command_prefix=',', intents=intents)

asyncio.run(bot.load_extension("dnd"))
@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Praise the code.')


bot.run(TOKEN)
