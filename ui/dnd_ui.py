import json
import asyncio
import discord
from settings import *
from discord.ui import Modal, Button, View, Select, TextInput, UserSelect
from discord.components import SelectOption
from settings import *
import spell


class CampaignUI(View):
    def __init__(self, bot, thread, host: discord.Member):
        super().__init__(timeout=None)

        self.host = host
        self.bot = bot
        self.thread = thread

        self.players = [self.host]
        self.characters = []

        invite_player = UserSelect(
            placeholder="Add Player",
        )
        invite_player.callback = self.invite_player

        remove_player = UserSelect(
            placeholder="Remove Player",
        )
        remove_player.callback = self.remove_player

        self.add_item(invite_player)
        self.add_item(remove_player)


    async def invite_player(self, interaction: discord.Interaction):
        player = interaction.data['values'][0]
        # make player into a discord.Member
        player = await self.bot.fetch_user(player)

        # check if the player is already in the game
        if player in self.players:
            await interaction.response.send_message(f"{player.name} is already in the game", ephemeral=True, delete_after=5)
            return
        if not self.is_registered(player.id):
            await interaction.response.send_message(f"{player.name} is not registered", ephemeral=True, delete_after=5)
            return
        self.players.append(player)
        character = self.get_character(player)
        self.characters.append(character)

        # invite the player to the thread
        await self.thread.add_recipient(player)

    async def remove_player(self, interaction: discord.Interaction):
        player = interaction.data['values'][0]
        # make player into a discord.Member
        player = await self.bot.fetch_user(player)

        # check if the player is already not in the game
        if player not in self.players:
            await interaction.response.send_message(f"{player.name} is not in the game", ephemeral=True, delete_after=5)
            return
        self.players.remove(player)
        character = self.get_character(player)
        self.characters.remove(character)

        # invite the player to the thread
        await self.thread.remove_recipient(player)


    def is_registered(self, player_id):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        return str(player_id) in characters

    def get_character(self, player):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        character = characters.get(str(player.id))
        return character
