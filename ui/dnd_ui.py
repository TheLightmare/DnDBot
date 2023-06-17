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
from world import World, City


INTERACTION_PRIVATE_MESSAGES = {}

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
        await self.thread.send(f"{player.mention}, you have joined the game ! Wait for the host to send the Campaign UI, then click on the button to get your own interface !", delete_after=10)

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

        # start the background tasks
        self.tasks.append(update_campaign_embed.start(message, self.get_character(self.host)))

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

        # load the world
        self.world = World()
        self.world.load()

        # load the quests
        self.quests = []

        # background tasks
        self.tasks = []


        # set the current location for each character
        if self.host_character.current_location is None:
            self.host_character.current_location = self.world.starting_location
            self.host_character.current_building = self.world.starting_location.buildings[0]
        for character in self.characters:
            character.current_location = self.world.starting_location
            character.current_building = self.world.starting_location.buildings[0]

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
        embed.add_field(name="Character", value=f"**Name:** {character.name}\n**Age:** {character.age}\n**Gold:** {character.gold}", inline=False)
        embed.add_field(name="CURRENT LOCATION", value=f"__{character.current_building.name}__ : {character.current_building.description}", inline=True)
        embed.add_field(name="PRESENT NPCS", value="", inline=True)
        embed.add_field(name="=========] ACTION LOG [=========", value="", inline=False)

        # send the embed
        await interaction.response.send_message(embed=embed, view=PlayerUI(interaction.user, character, self.thread), ephemeral=True)
        # add the player to the players with ui
        self.players_with_ui[interaction.user] = True

        # start the background tasks
        message = await interaction.original_response()
        INTERACTION_PRIVATE_MESSAGES[interaction.user] = message
        self.tasks.append(update_personal_embed.start(message, self.get_character(interaction.user)))

    def get_character(self, player):
        for character in self.characters:
            if character.author == player:
                return character

@tasks.loop(seconds=2)
async def update_campaign_embed(message, host_character: Character):
    # update the embed
    embed = message.embeds[0]
    embed.set_field_at(0, name="CURRENT LOCATION", value=f"__{host_character.current_location.name}__ : {host_character.current_location.description}", inline=True)


    # modify the message
    await message.edit(embed=embed)

@tasks.loop(seconds=2)
async def update_personal_embed(message, character: Character):
    # update the embed
    embed = message.embeds[0]
    embed.set_field_at(1,
                    name="CURRENT LOCATION",
                    value=f"__{character.current_building.name}__ : {character.current_building.description}",
                    inline=True)

    npcs = character.current_building.get_present_npcs()
    npc_string = ""
    for npc in npcs:
        npc_string += f"- {npc.name} : {npc.description}\n"
    embed.set_field_at(2,
                       name="PRESENT NPCS",
                       value=npc_string,
                       inline=True)

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
    def __init__(self, player, character: Character, thread: discord.Thread):
        super().__init__(timeout=None)

        self.player = player
        self.character = character
        self.thread = thread

        # npc the player is talking to
        self.talking_to = None

        self.action_log = []

        # buttons
        move_button = Button(
            label="Move",
            style=discord.ButtonStyle.blurple,
        )
        move_button.callback = self.move

        talk_button = Button(
            label="Talk/Continue Talking",
            style=discord.ButtonStyle.blurple,
        )
        talk_button.callback = self.talk

        # select menus

        npc_list = self.character.current_building.get_present_npcs()
        npc_options = []
        for npc in npc_list:
            npc_options.append(SelectOption(label=npc.name, value=npc.id, description=npc.description))
        if npc_options == []:
            npc_options.append(SelectOption(label="No NPCs", value="No NPCs", description="There are no NPCs here"))
        select_npc = Select(placeholder="Select an NPC to talk to", options=npc_options, min_values=1, max_values=1)
        select_npc.callback = self.talk_to_npc

        # all of this crap is for the spell selection
        spells_list = self.character.get_spells_dict()
        spell_options = []
        for spell in spells_list:
            spell_options.append(SelectOption(label=spell["name"], value=spell["name"], description=spell["description"]))
        if spell_options == []:
            spell_options.append(SelectOption(label="No Spells", value="No Spells", description="You don't have any spells"))
        spell_select = Select(placeholder="Select a Spell", options=spell_options, min_values=1, max_values=1)
        spell_select.callback = self.cast_spell

        # add the buttons and select menus
        self.add_item(move_button)
        self.add_item(talk_button)
        self.add_item(select_npc)
        self.add_item(spell_select)

    def add_to_action_log(self, message):
        self.action_log.append(message)

        if len(self.action_log) >= 6:
            self.action_log.pop(0)

    def display_action_log(self):
        # display the action log in a code block
        log = "```"
        for message in self.action_log:
            log += message + "\n"
        return log + "```"

    async def move(self, interaction: discord.Interaction):
        await interaction.response.defer()

    async def talk_to_npc(self, interaction: discord.Interaction):
        if self.talking_to is not None:
            await interaction.response.send_message("You are already talking to an NPC, exhaust current dialogue first", ephemeral=True, delete_after=5)
            return

        # get the npc
        npc = self.character.current_building.get_npc(interaction.data["values"][0])

        self.talking_to = npc

        # modify the embed
        message = INTERACTION_PRIVATE_MESSAGES[self.player]
        embed = message.embeds[0]

        self.add_to_action_log(f"<You approach {npc.name}, and start a conversation...>")
        embed.set_field_at(3, name="=========] ACTION LOG [=========", value=self.display_action_log(), inline=False)
        await message.edit(embed=embed)
        await interaction.response.defer()


    async def cast_spell(self, interaction: discord.Interaction):
        await interaction.response.defer()


    async def talk(self, interaction: discord.Interaction):
        if self.talking_to is None:
            await interaction.response.send_message("You are not talking to an NPC", ephemeral=True, delete_after=5)
            return

        # get the npc
        npc = self.talking_to

        # get the message
        message = INTERACTION_PRIVATE_MESSAGES[self.player]
        embed = message.embeds[0]

        # get the dialogue
        dialogue = npc.talk()
        if dialogue == None:
            dialogue = "You have exhausted this NPC's dialogue"
            self.add_to_action_log(f'{dialogue}')
            self.talking_to = None
        else :
            self.add_to_action_log(f'{npc.name} : "{dialogue}"')

        # modify the embed
        embed.set_field_at(3, name="=========] ACTION LOG [=========", value=self.display_action_log(), inline=False)
        await message.edit(embed=embed)
        await interaction.response.defer()

