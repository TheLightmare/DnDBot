import json
import random

import discord
from discord.ext import commands
from discord import app_commands

from util import misc_utils
from character import Character
from play import Play
from ui import character_ui
from util.settings import *

class Misc_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Miscellaneous Cog loaded successfully')


    @app_commands.command(name="r", description="Roll a dice")
    async def roll(self, interaction : discord.Interaction, maxint : int):
        dice = random.randint(1, maxint)
        message_content = f":game_die: {interaction.user.mention} rolled a `{dice}/{maxint}`"

        # append an appreciation message
        if dice == maxint:
            message_content += " Critical Success ! :D"
        elif dice == 1:
            message_content += " Critical Failure ! :("
        elif dice > maxint/2:
            message_content += " Nice !"
        elif dice < maxint/2:
            message_content += " Oof."

        # send the message
        await interaction.response.send_message(message_content)


async def setup(bot):
    await bot.add_cog(Misc_Cog(bot))