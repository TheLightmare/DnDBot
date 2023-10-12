import random

import discord
from discord.ui import Button, View, Select, UserSelect, Modal, TextInput
from discord.components import SelectOption
from misc_utils import *
from character import Character
from ui.trade_ui import TradeUI
from world import World
from util.dice import Dice

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
        self.tasks.append(player_chat.start(self.thread, self.players))


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

        await interaction.response.defer()


    async def remove_player(self, interaction: discord.Interaction):
        # check if the one who invited is the host
        if interaction.user != self.host:
            await interaction.response.send_message("You are not the host", ephemeral=True, delete_after=5)
            return

        player = interaction.data['values'][0]
        # make player into a discord.Member
        player = await self.bot.fetch_user(player)

        # check if the player is self
        if player == interaction.user:
            await interaction.response.send_message("You cannot remove yourself ! Use the 'Leave' button for that !", ephemeral=True, delete_after=5)
            return

        # check if the player is already not in the game
        if player not in self.players:
            await interaction.response.send_message(f"{player.name} is not in the game", ephemeral=True, delete_after=5)
            return
        self.players.remove(player)

        self.characters.remove(self.get_character(player))

        # remove the player from the thread
        await self.thread.remove_user(player)

        await interaction.response.defer()


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
        self.world = World()
        message = await self.thread.send(embed=embed, view=CampaignUI(self.bot, self.thread, self.players, self.host, self.characters, self.world))

        # start the background tasks
        self.tasks.append(update_campaign_embed.start(message, self.get_character(self.host), world=self.world))

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
            # update the embed
            embed = interaction.message.embeds[0]
            embed.set_field_at(0, name="Host", value=self.host.mention, inline=False)
            await interaction.message.edit(embed=embed)
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
    def __init__(self, bot, thread: discord.Thread, party: list, host: discord.Member, characters: list, world: World):
        super().__init__(timeout=None)
        self.bot = bot
        self.thread = thread
        self.party = party
        self.host = host
        self.characters = characters
        self.host_character = self.get_character(self.host)

        # load the world
        self.world = world

        # load the quests
        self.quests = []

        # background tasks
        self.tasks = []

        # player ui list
        self.player_ui_list = []

        # set the current location for each character
        for character in self.characters:
            character.current_location = self.world.starting_location
            character.current_building = self.world.starting_location.buildings[0]
            # add character to the list of the location and building
            character.current_location.add_player(character)
            character.current_building.add_player(character)

        self.players_with_ui = {}
        get_personal_ui = Button(
            label="Get Personal UI",
            style=discord.ButtonStyle.blurple,
        )
        get_personal_ui.callback = self.get_personal_ui

        move_party_options = []
        for location in self.world.cities:
            move_party_options.append(SelectOption(label=location.name, value=location.id, description=""))

        move_party = Select(
            placeholder="Select where to move party",
            options=move_party_options,
            min_values=1,
            max_values=1
        )
        move_party.callback = self.move_party


        self.add_item(get_personal_ui)
        self.add_item(move_party)


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
        embed.add_field(name="PRESENT NPCs", value="", inline=True)
        embed.add_field(name="PRESENT PLAYERS", value="", inline=True)
        embed.add_field(name="=========] ACTION LOG [=========", value="", inline=False)

        # create the UI
        player_ui = PlayerUI(interaction.user, character, self.thread, self.world)

        # send the embed
        await interaction.response.send_message(embed=embed, view=player_ui, ephemeral=True)
        # add the player to the players with ui
        self.players_with_ui[interaction.user] = True
        # add the ui to the list
        self.player_ui_list.append(player_ui)


        # start the background tasks
        message = await interaction.original_response()
        INTERACTION_PRIVATE_MESSAGES[interaction.user] = message
        self.tasks.append(update_personal_embed.start(message, self.get_character(interaction.user)))


    async def move_party(self, interaction: discord.Interaction):
        # check if the player is the host
        if interaction.user != self.host:
            await interaction.response.send_message("Only the host can move the party", ephemeral=True, delete_after=5)
            return
        # check if the whole party is in the same location
        for character in self.characters:
            if character.current_location != self.characters[0].current_location:
                await interaction.response.send_message("The whole party must be in the same location to move", ephemeral=True, delete_after=5)
                return

        # get the location
        location = self.world.get_node(interaction.data['values'][0])

        # move the party
        for character in self.characters:
            # update the location
            character.current_location.remove_player(character)
            character.current_location = location
            character.current_location.add_player(character)
            # update the building
            character.current_building.remove_player(character)
            character.current_building = character.current_location.buildings[0]
            character.current_building.add_player(character)



        # update the embed
        embed = interaction.message.embeds[0]
        embed.set_field_at(0, name="CURRENT LOCATION", value=f"__{location.name}__ : {location.description}", inline=True)

        # modify the message
        await interaction.message.edit(embed=embed)

        # update players npc and building lists
        for player_ui in self.player_ui_list:
            await player_ui.update_npc_list()
            await player_ui.update_building_list()

        await interaction.response.defer()


    def get_character(self, player):
        for character in self.characters:
            if character.author == player:
                return character

@tasks.loop(seconds=2)
async def update_campaign_embed(message, host_character: Character, world: World):
    # update the embed
    embed = message.embeds[0]
    embed.set_field_at(0, name="CURRENT LOCATION", value=f"__{host_character.current_location.name}__ : {host_character.current_location.description}", inline=True)
    embed.set_field_at(1, name="CURRENT TIME", value=f"{world.time}", inline=True)

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
                       name="PRESENT NPCs",
                       value=npc_string,
                       inline=True)

    players = character.current_building.get_present_players()
    player_string = ""
    for player in players:
        player_string += f"- {player.name}\n"
    embed.set_field_at(3,
                          name="PRESENT PLAYERS",
                          value=player_string,
                          inline=True)

    # modify the message if it still exists (should happen only if the thread got deleted)
    try:
        await message.edit(embed=embed)
    except discord.errors.NotFound:
        pass

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
    def __init__(self, player : discord.User, character: Character, thread: discord.Thread, world: World):
        super().__init__(timeout=None)

        self.player = player
        self.character = character
        self.thread = thread
        self.world = world

        self.d20 = Dice(20)

        # npc the player is talking to
        self.talking_to = None

        # action log
        self.action_log = []
        # index of the action log (0 or more)
        self.action_log_index = 0

        # buttons
        talk_button = Button(
            label="Talk/Continue Talking",
            style=discord.ButtonStyle.blurple,
        )
        talk_button.callback = self.talk

        scroll_up_button = Button(
            label="Scroll Up",
            emoji="⬆️",
            style=discord.ButtonStyle.blurple,
        )
        scroll_up_button.callback = self.scroll_up

        scroll_down_button = Button(
            label="Scroll Down",
            emoji="⬇️",
            style=discord.ButtonStyle.blurple,
        )
        scroll_down_button.callback = self.scroll_down

        scroll_top_button = Button(
            label="Scroll to Top",
            emoji="🔝",
            style=discord.ButtonStyle.blurple,
        )
        scroll_top_button.callback = self.scroll_top

        scroll_bottom_button = Button(
            label="Scroll to Bottom",
            emoji="🔚",
            style=discord.ButtonStyle.blurple,
        )
        scroll_bottom_button.callback = self.scroll_bottom

        # select menus

        npc_list = self.character.current_building.get_present_npcs()
        npc_options = []
        for npc in npc_list:
            npc_options.append(SelectOption(label=npc.name, value=npc.id, description=npc.description))
        if npc_options == []:
            npc_options.append(SelectOption(label="No NPCs", value="No NPCs", description="There are no NPCs here"))
        self.select_npc = Select(placeholder="Select an NPC to talk to", options=npc_options, min_values=1, max_values=1)
        self.select_npc.callback = self.talk_to_npc


        building_options = []
        for building in self.character.current_building.city.buildings:
            building_options.append(SelectOption(label=building.name, value=building.id, description=""))
        self.building_select = Select(placeholder="Where do you want to go ?", options=building_options, min_values=1,
                                 max_values=1)
        self.building_select.callback = self.move_to_building

        # contextual actions
        action_list = [
            SelectOption(label="Hide", value="hide", description="Find a place to hide"),
            SelectOption(label="Rest", value="rest", description="Take a Short Rest")
        ]
        self.select_action = Select(placeholder="Contextual actions", options=action_list, min_values=1, max_values=1)
        self.select_action.callback = self.do_action


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
        self.add_item(talk_button)
        self.add_item(scroll_up_button)
        self.add_item(scroll_down_button)
        self.add_item(scroll_top_button)
        self.add_item(scroll_bottom_button)
        self.add_item(self.select_npc)
        self.add_item(self.select_action)
        self.add_item(self.building_select)
        self.add_item(spell_select)

    def add_to_action_log(self, message, color_ansi = ""):
        if color_ansi == "":
            self.action_log.append(message)
        else:
            self.action_log.append(color_ansi + message + "\u001b[0m")

        if len(self.action_log) >= 100:
            self.action_log.pop(0)

    # returns the action log as a string
    def display_action_log(self):
        # display the action log in a code block
        log = "```ansi\n"
        maxrange = min(6, len(self.action_log))
        for i in range(maxrange):
            log += self.action_log[len(self.action_log) - maxrange - self.action_log_index + i] + "\n"

        return log + "```"

    async def scroll_up(self, interaction: discord.Interaction):
        if self.action_log_index + 6 < len(self.action_log):
            self.action_log_index += 1
            embed = INTERACTION_PRIVATE_MESSAGES[self.player].embeds[0]
            embed.set_field_at(4, name="=========] ACTION LOG [=========", value=self.display_action_log(),
                               inline=False)
            await interaction.response.edit_message(embed=embed)
        else :
            await interaction.response.defer()

    async def scroll_down(self, interaction: discord.Interaction):
        if self.action_log_index > 0:
            self.action_log_index -= 1
            embed = INTERACTION_PRIVATE_MESSAGES[self.player].embeds[0]
            embed.set_field_at(4, name="=========] ACTION LOG [=========", value=self.display_action_log(),
                               inline=False)
            await interaction.response.edit_message(embed=embed)
        else :
            await interaction.response.defer()

    async def scroll_top(self, interaction: discord.Interaction):
        if len(self.action_log) > 6:
            self.action_log_index = len(self.action_log) - 6
        embed = INTERACTION_PRIVATE_MESSAGES[self.player].embeds[0]
        embed.set_field_at(4, name="=========] ACTION LOG [=========", value=self.display_action_log(),
                           inline=False)
        await interaction.response.edit_message(embed=embed)

    async def scroll_bottom(self, interaction: discord.Interaction):
        self.action_log_index = 0
        embed = INTERACTION_PRIVATE_MESSAGES[self.player].embeds[0]
        embed.set_field_at(4, name="=========] ACTION LOG [=========", value=self.display_action_log(),
                           inline=False)
        await interaction.response.edit_message(embed=embed)

    async def update_actions_list(self):
        # update the action list
        action_list = [
            SelectOption(label="Hide", value="hide", description="Find a place to hide"),
            SelectOption(label="Rest", value="rest", description="Take a Short Rest")
        ]
        # if the player is talking to a npc
        if self.talking_to is not None:
            action_list.append(SelectOption(label="Attack", value="attack", description="Attack the NPC"))
            action_list.append(SelectOption(label="Steal", value="steal", description="Attempt to steal from the NPC"))
            action_list.append(SelectOption(label="Demand Quest", value="demand_quest", description="Demand a quest from the NPC"))
            action_list.append(SelectOption(label="Demand Trade", value="demand_trade", description="Demand a trade from the NPC"))

        self.select_action.options = action_list

        # update the message
        message = INTERACTION_PRIVATE_MESSAGES[self.player]
        await message.edit(view=self)

    async def update_npc_list(self):
        # update the npc list
        npc_list = self.character.current_building.get_present_npcs()
        npc_options = []
        for npc in npc_list:
            npc_options.append(SelectOption(label=npc.name, value=npc.id, description=npc.description))
        if npc_options == []:
            npc_options.append(SelectOption(label="No NPCs", value="No NPCs", description="There are no NPCs here"))
        self.select_npc.options = npc_options

        # update the message
        message = INTERACTION_PRIVATE_MESSAGES[self.player]
        await message.edit(view=self)

    async def update_building_list(self):
        # update the building list
        building_options = []
        for building in self.character.current_building.city.buildings:
            building_options.append(SelectOption(label=building.name, value=building.id, description=""))
        if building_options == []:
            building_options.append(SelectOption(label="No Buildings", value="No Buildings", description="There are no Buildings here"))
        self.building_select.options = building_options

        # update the message
        message = INTERACTION_PRIVATE_MESSAGES[self.player]
        await message.edit(view=self)


    async def do_action(self, interaction: discord.Interaction):
        npc = self.talking_to
        action = interaction.data["values"][0]

        if action == "steal" and npc is not None:
            if self.d20.ability_check(self.character, "dexterity"):
                self.add_to_action_log(f"<You manage to steal {random.randint(1, npc.gold)} from {npc.name}>")
            else:
                self.add_to_action_log(f"<You got caught, but nothing happens>")
        elif action == "demand_quest":
            self.add_to_action_log(npc.give_quest())
        elif action == "demand_trade":
            # create the trade message
            # TODO: this does not work for some reason
            await interaction.response.send_message(
                f"{self.character.name} offers {npc.name} a trade",
                view=TradeUI(self.player, self.character, npc, self),
                ephemeral=True
            )
            return
        # general actions
        elif action == "attack" and npc is not None:
            # TODO: connect to the combat system
            if self.d20.attack_roll(self.character, npc):
                self.add_to_action_log(f"<You hit {npc.name} for {random.randint(1, 6)} damage>")
            else:
                self.add_to_action_log(f"<You miss {npc.name}>")
        elif action == "hide":
            if self.d20.ability_check(self.character, "dexterity"):
                self.add_to_action_log(f"<You manage to hide>")
            else:
                self.add_to_action_log(f"<You got caught, but nothing happens>")
        elif action == "rest":
            self.add_to_action_log(f"<You take a short rest>")

        # update the embed
        message = INTERACTION_PRIVATE_MESSAGES[self.player]
        embed = message.embeds[0]
        embed.set_field_at(4, name="=========] ACTION LOG [=========", value=self.display_action_log(), inline=False)
        await message.edit(embed=embed)
        await interaction.response.defer()

    # callback for the building select menu, only called when the player is moving
    async def move_to_building(self, interaction: discord.Interaction):
        # get the building object
        building = self.character.current_location.get_building(interaction.data["values"][0])

        # remove player from the current building
        self.character.current_building.remove_player(self.character)

        # move the player
        self.character.move_building(building)
        self.add_to_action_log(f"<You move to {building.name}>")
        embed = INTERACTION_PRIVATE_MESSAGES[self.player].embeds[0]
        embed.set_field_at(4, name="=========] ACTION LOG [=========", value=self.display_action_log(), inline=False)

        # remove the select menu
        message = INTERACTION_PRIVATE_MESSAGES[self.player]
        await message.edit(view=self, embed=embed)

        # update the lists of actions and npcs
        await self.update_actions_list()
        await self.update_npc_list()

        await interaction.response.defer()

    async def talk_to_npc(self, interaction: discord.Interaction):
        if self.talking_to is not None:
            await interaction.response.send_message("You are already talking to an NPC, exhaust current dialogue first", ephemeral=True, delete_after=5)
            return

        # get the npc
        npc = self.character.current_building.get_npc(interaction.data["values"][0])

        # set the npc you interact with
        self.talking_to = npc

        # update the contextual actions
        await self.update_actions_list()

        # modify the embed
        message = INTERACTION_PRIVATE_MESSAGES[self.player]
        embed = message.embeds[0]

        self.add_to_action_log(f"<You approach {npc.name}, and start a conversation...>")
        embed.set_field_at(4, name="=========] ACTION LOG [=========", value=self.display_action_log(), inline=False)
        await message.edit(embed=embed)
        await interaction.response.defer()


    async def cast_spell(self, interaction: discord.Interaction):
        # get the spell
        spell = self.character.get_spell(interaction.data["values"][0])

        # ability check
        #TODO : add ability check

        # get the message
        message = INTERACTION_PRIVATE_MESSAGES[self.player]
        embed = message.embeds[0]

        # get the spell result
        spell_result = spell.cast(self.character)
        self.add_to_action_log(f'<{spell_result}>')
        embed.set_field_at(4, name="=========] ACTION LOG [=========", value=self.display_action_log(), inline=False)

        # modify the embed
        await message.edit(embed=embed)

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
        (dialogue, is_end) = npc.talk()
        if is_end:
            self.add_to_action_log(f"<You finished talking to {npc.name}>")
            self.talking_to = None

            # update the contextual actions
            await self.update_actions_list()

        else :
            self.add_to_action_log(f'{npc.name} : "{dialogue}"')

        # modify the embed
        embed.set_field_at(4, name="=========] ACTION LOG [=========", value=self.display_action_log(), inline=False)
        await message.edit(embed=embed)
        await interaction.response.defer()





# =========================] MODALS [=========================
