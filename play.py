import discord
from discord.ext import commands, tasks
import json
from settings import *
import ui.dnd_ui

class Play():
    def __init__(self, bot, thread, host: discord.Member):
        self.bot = bot
        self.thread = thread
        self.host = host

        self.players = [self.host]
        self.characters = []

    async def start(self):
        # create the common embed
        common_embed = discord.Embed(title="DnD", description="Welcome to the game", color=0x00ff00)
        common_embed.add_field(name="Host", value=self.host.mention, inline=False)
        common_embed.add_field(name="Players", value=" ".join([player.mention for player in self.players]), inline=False)

        # send the embed
        await self.thread.send(embed=common_embed, view=ui.dnd_ui.LobbyUI(self.bot, self.thread, self.host))

    # background tasks

