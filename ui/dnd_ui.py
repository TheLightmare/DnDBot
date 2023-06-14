import json
import asyncio
import discord
from settings import *
from discord.ui import Modal, Button, View, Select, TextInput, UserSelect
from discord.components import SelectOption
from settings import *
import spell
from character import Character

class CampaignUI(View):
    def __init__(self, bot, thread, host: discord.Member):
        super().__init__(timeout=None)

        self.host = host
        self.bot = bot
        self.thread = thread

        self.players = [self.host]
        character = Character(self.host)
        character.load()
        self.characters = [character]

        invite_player = UserSelect(
            placeholder="Add Player",
        )
        invite_player.callback = self.invite_player

        remove_player = UserSelect(
            placeholder="Remove Player",
        )
        remove_player.callback = self.remove_player

        get_personal_ui = Button(
            label="Get Personal UI",
            style=discord.ButtonStyle.blurple,
        )
        get_personal_ui.callback = self.get_personal_ui

        self.add_item(invite_player)
        self.add_item(remove_player)
        self.add_item(get_personal_ui)


    async def invite_player(self, interaction: discord.Interaction):
        # check if the one who invited is the host
        if interaction.user != self.host:
            await interaction.response.send_message("You are not the host", ephemeral=True, delete_after=5)
            return

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
        character = Character(player)
        character.load()
        self.characters.append(character)

        # invite the player to the thread
        await self.thread.add_recipient(player)

        # send a message in the thread to the player
        await self.thread.send(f"{player.mention}, you have joined the game ! You can now use the buttons above to get your personal UI !", delete_after=10)


    async def remove_player(self, interaction: discord.Interaction):
        # check if the one who invited is the host
        if interaction.user != self.host:
            await interaction.response.send_message("You are not the host", ephemeral=True, delete_after=5)
            return

        player = interaction.data['values'][0]
        # make player into a discord.Member
        player = await self.bot.fetch_user(player)

        # check if the player is already not in the game
        if player not in self.players:
            await interaction.response.send_message(f"{player.name} is not in the game", ephemeral=True, delete_after=5)
            return
        self.players.remove(player)

        self.characters.remove(self.get_character(player))

        # invite the player to the thread
        await self.thread.remove_recipient(player)



    async def get_personal_ui(self, interaction: discord.Interaction):
        # create the embed
        embed = discord.Embed(title=f"{interaction.user} Personal UI", description="This is your personal interface", color=0x00ff00)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        character = self.get_character(interaction.user)
        embed.add_field(name="Character", value=f"**Name:** {character.name}\n**Age:** {character.age}", inline=False)

        # send the embed
        await interaction.response.send_message(embed=embed, view=PlayerUI(interaction.user), ephemeral=True)




    def is_registered(self, player_id):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        return str(player_id) in characters

    def get_character(self, player):
        for character in self.characters:
            if character.author == player:
                return character


class PlayerUI(View):
    def __init__(self, player):
        super().__init__(timeout=None)

        self.player = player
