import json
import asyncio
import discord
from settings import *
from discord.ui import Modal, Button, View, Select, TextInput, UserSelect
from discord.components import SelectOption
from discord.ext import commands, tasks
from settings import *
import spell
from character import Character
from world import World

class LobbyUI(View):
    def __init__(self, bot, thread: discord.Thread, host: discord.Member, tasks: list = []):
        super().__init__(timeout=None)

        self.host = host
        self.bot = bot
        self.thread = thread
        self.tasks = tasks

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

        START_CAMPAIGN = Button(
            label="Start Campaign",
            style=discord.ButtonStyle.green
        )
        START_CAMPAIGN.callback = self.start_campaign

        LEAVE = Button(
            label="Leave",
            style=discord.ButtonStyle.red
        )
        LEAVE.callback = self.leave

        self.add_item(invite_player)
        self.add_item(remove_player)
        self.add_item(START_CAMPAIGN)
        self.add_item(LEAVE)

        # background tasks
        player_chat.start(self.thread, self.players)


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
        await self.thread.add_user(player)

        # send a message in the thread to the player
        await self.thread.send(f"{player.mention}, you have joined the game ! You can now use the buttons above to get your personal UI !", delete_after=10)

        # update the embed
        embed = interaction.message.embeds[0]
        embed.set_field_at(1, name="Players", value=" ".join([player.mention for player in self.players]), inline=False)
        await interaction.message.edit(embed=embed)


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

        # remove the player from the thread
        await self.thread.remove_user(player)

    async def start_campaign(self, interaction: discord.Interaction):
        # check if the one who invited is the host
        if interaction.user != self.host:
            await interaction.response.send_message("You are not the host", ephemeral=True, delete_after=5)
            return

        # create the embed
        embed = discord.Embed(title="Campaign UI", description="This is the campaign interface", color=0x00ff00)
        embed.add_field(name="CURRENT LOCATION", value="", inline=True)
        embed.add_field(name="CURRENT TIME", value="", inline=True)
        embed.add_field(name="CURRENT WEATHER", value="", inline=True)
        embed.add_field(name="CURRENT TEMPERATURE", value="", inline=True)

        embed.add_field(name="MAP OF SURROUNDINGS", value="", inline=False)

        # send the embed
        message = await self.thread.send(embed=embed, view=CampaignUI(self.bot, self.thread, self.players, self.host, self.characters))
        self.tasks.append(update_embed.start(message, self.get_character(self.host)))

        await interaction.response.defer()

    async def leave(self, interaction: discord.Interaction):
        # remove the player from the game
        self.players.remove(interaction.user)

        self.characters.remove(self.get_character(interaction.user))

        # remove the player from the thread
        await self.thread.remove_user(interaction.user)

        # send a message in the thread to the player
        await self.thread.send(f"{interaction.user} left the game !", delete_after=10)

        # check if no one is left
        if len(self.players) == 0:
            # delete the thread
            await self.thread.delete()
            # terminate the tasks
            for task in self.tasks:
                task.cancel()
            return

        # check if the host left
        if interaction.user == self.host:
            # make the first player the host
            self.host = self.players[0]
            # send a message in the thread to the player
            await self.thread.send(f"{self.host} is now the host !", delete_after=10)


    def is_registered(self, player_id):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        return str(player_id) in characters

    def get_character(self, player):
        for character in self.characters:
            if character.author == player:
                return character



#UI for the campaign
class CampaignUI(View):
    def __init__(self, bot, thread: discord.Thread, party: list, host: discord.Member, characters: list):
        super().__init__(timeout=None)
        self.bot = bot
        self.thread = thread
        self.party = party
        self.host = host
        self.characters = characters
        self.host_character = self.get_character(self.host)

        self.world = World()
        self.world.load()

        # set the current location for each character
        if self.host_character.current_location is None:
            self.host_character.current_location = self.world.starting_location
        for character in self.characters:
            character.current_location = self.world.starting_location

        self.players_with_ui = {}
        get_personal_ui = Button(
            label="Get Personal UI",
            style=discord.ButtonStyle.blurple,
        )
        get_personal_ui.callback = self.get_personal_ui

        self.add_item(get_personal_ui)



    async def get_personal_ui(self, interaction: discord.Interaction):
        # check if the player already has a ui
        if interaction.user in self.players_with_ui:
            await interaction.response.send_message("You already have a personal UI", ephemeral=True, delete_after=5)
            return
        # create the embed
        embed = discord.Embed(title=f"{interaction.user} Personal UI", description="This is your personal interface", color=0x00ff00)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        character = self.get_character(interaction.user)
        embed.add_field(name="Character", value=f"**Name:** {character.name}\n**Age:** {character.age}", inline=False)

        # send the embed
        await interaction.response.send_message(embed=embed, view=PlayerUI(interaction.user, character), ephemeral=True)
        # add the player to the players with ui
        self.players_with_ui[interaction.user] = True

    def get_character(self, player):
        for character in self.characters:
            if character.author == player:
                return character

@tasks.loop(seconds=2)
async def update_embed(message, host_character: Character):
    # update the embed
    embed = message.embeds[0]
    embed.set_field_at(0, name="CURRENT LOCATION", value=host_character.current_location.name, inline=True)

    # modify the message
    await message.edit(embed=embed)

@tasks.loop(seconds=1)
async def player_chat(thread: discord.Thread, players: list):
    messages = []
    async for message in thread.history():
        if message.author in players:
            messages.append(message)

            if len(messages) >= 6:
                msg = messages.pop()
                await msg.delete()

class PlayerUI(View):
    def __init__(self, player, character: Character):
        super().__init__(timeout=None)

        self.player = player
        self.character = character


