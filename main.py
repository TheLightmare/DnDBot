import json

import asyncio
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot

#==== NECESSARY STUFF ====
intents = discord.Intents.all()
TOKEN = "Nzk2NjM2NDc1NjA0NDY3NzEy.GXNmLE.oeTqYvwR2UipbQBM3sMAkeEe61Axv2Z0IKva30"
bot = commands.Bot(command_prefix=',', intents=intents)

asyncio.run(bot.load_extension("dnd"))
@bot.event
async def on_ready():
    print('Bot s ready')


bot.run(TOKEN)
