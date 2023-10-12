from discord.components import SelectOption
from discord.ui import Button, View, Select

from misc_utils import *
from ui.player_ui import PlayerUI
from world import World

INTERACTION_PRIVATE_MESSAGES = {}


# UI for the campaign
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

        self.add_item(move_party)
        self.add_item(get_personal_ui)


    async def get_personal_ui(self, interaction: discord.Interaction):
        # check if the player already has a ui
        if interaction.user in self.players_with_ui:
            await interaction.response.send_message("You already have a personal UI", ephemeral=True, delete_after=5)
            return
        # create the embed
        embed = discord.Embed(title=f"{interaction.user} Personal UI", description="This is your personal interface",
                              color=0x00ff00)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        character = self.get_character(interaction.user)
        embed.add_field(name="Character",
                        value=f"**Name:** {character.name}\n**Age:** {character.age}\n**Gold:** {character.gold}",
                        inline=False)
        embed.add_field(name="CURRENT LOCATION",
                        value=f"__{character.current_building.name}__ : {character.current_building.description}",
                        inline=True)
        embed.add_field(name="PRESENT NPCs", value="", inline=True)
        embed.add_field(name="PRESENT PLAYERS", value="", inline=True)
        embed.add_field(name="=========] ACTION LOG [=========", value="", inline=False)

        # create the UI
        player_ui = PlayerUI(interaction.user, character, self.thread, self.world)
        # send the embed
        await interaction.response.send_message(embed=embed, view=player_ui, ephemeral=True)

        # set the message and start the background tasks
        player_ui.message = await interaction.original_response()
        player_ui.update_personal_embed.start()

        # add the player to the players with ui
        self.players_with_ui[interaction.user] = True
        # add the ui to the list
        self.player_ui_list.append(player_ui)

        # start the background tasks
        message = await interaction.original_response()
        INTERACTION_PRIVATE_MESSAGES[interaction.user] = message

    async def move_party(self, interaction: discord.Interaction):
        # check if the player is the host
        if interaction.user != self.host:
            await interaction.response.send_message("Only the host can move the party", ephemeral=True, delete_after=5)
            return
        # check if the whole party is in the same location
        for character in self.characters:
            if character.current_location != self.characters[0].current_location:
                await interaction.response.send_message("The whole party must be in the same location to move",
                                                        ephemeral=True, delete_after=5)
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
        embed.set_field_at(0, name="CURRENT LOCATION", value=f"__{location.name}__ : {location.description}",
                           inline=True)

        # modify the message
        await interaction.message.edit(embed=embed)

        # update players npc and building lists
        for player_ui in self.player_ui_list:
            await player_ui.update_npc_list()
            await player_ui.update_building_list()
            # add to the action log
            player_ui.add_to_action_log(f"<The party moved to {location.name}>")
            await player_ui.display_action_log()

        await interaction.response.defer()

    def get_character(self, player):
        for character in self.characters:
            if character.author == player:
                return character

