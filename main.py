import json

import asyncio
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot

#==== NECESSARY STUFF ====
intents = discord.Intents.all()
TOKEN = "Nzk2NjM2NDc1NjA0NDY3NzEy.Gs-YI1.0BTUM-0crSTpscdIoVT5QYVB_K1Qx84Sps7vJA"
bot = commands.Bot(command_prefix=',', intents=intents)

asyncio.run(bot.load_extension("dnd"))
@bot.event
async def on_ready():
    print('Bot s ready')


bot.run(TOKEN)
