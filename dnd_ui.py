import json
import asyncio
import discord
from discord.ui import Button, View, Select
from settings import *


class StatDistributionUI(View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(label="TestButton", style=discord.ButtonStyle.blurple)
    async def name(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("TestMessage")


    @discord.ui.select(options=[discord.SelectOption(label="TestOption", value="TestValue")], placeholder="TestPlaceholder")
    async def test(self, interactionresponse: discord.InteractionResponse):
        await interactionresponse.send_message()