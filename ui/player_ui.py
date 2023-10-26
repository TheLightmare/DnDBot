import random

from discord.ui import Button, View, Select
from discord.components import SelectOption
from util.misc_utils import *
from character import Character
from ui.trade_ui import TradeUI
from world.world import World
from util.dice import Dice

class PlayerUI(View):
    def __init__(self, player : discord.User, character: Character, thread: discord.Thread, world: World):
        super().__init__(timeout=None)

        self.player = player
        self.character = character
        self.thread = thread
        self.world = world

        self.message = None

        self.d20 = Dice(20)

        # npc the player is talking to
        self.talking_to = None
        # index of the current dialogue line for every npc
        self.npc_dialogue_indexes = []

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

    # displays the action log in a code block
    async def display_action_log(self):
        # display the action log in a code block
        log = "```ansi\n"
        maxrange = min(6, len(self.action_log))
        for i in range(maxrange):
            log += self.action_log[len(self.action_log) - maxrange - self.action_log_index + i] + "\n"

        log += "```"

        embed = self.message.embeds[0]
        embed.set_field_at(4, name="=========] ACTION LOG [=========", value=log, inline=False)
        await self.message.edit(embed=embed)



    async def scroll_up(self, interaction: discord.Interaction):
        if self.action_log_index + 6 < len(self.action_log):
            self.action_log_index += 1
            embed = self.message.embeds[0]
            await self.display_action_log()
        await interaction.response.defer()

    async def scroll_down(self, interaction: discord.Interaction):
        if self.action_log_index > 0:
            self.action_log_index -= 1
            embed = self.message.embeds[0]
            await self.display_action_log()
        await interaction.response.defer()


    async def scroll_top(self, interaction: discord.Interaction):
        if len(self.action_log) > 6:
            self.action_log_index = len(self.action_log) - 6
        await self.display_action_log()
        await interaction.response.defer()


    async def scroll_bottom(self, interaction: discord.Interaction):
        self.action_log_index = 0
        await self.display_action_log()
        await interaction.response.defer()

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
        message = self.message
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
        message = self.message
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
        message = self.message
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
        await self.display_action_log()

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
        embed = self.message.embeds[0]
        await self.display_action_log()

        # remove the select menu
        message = self.message
        await message.edit(view=self, embed=embed)

        # update the embed
        await self.update_personal_embed()

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
        message = self.message
        embed = message.embeds[0]

        self.add_to_action_log(f"<You approach {npc.name}, and start a conversation...>")
        await self.display_action_log()

        await interaction.response.defer()


    async def cast_spell(self, interaction: discord.Interaction):
        # get the spell
        spell = self.character.get_spell(interaction.data["values"][0])

        # ability check
        #TODO : add ability check

        # get the spell result
        spell_result = spell.cast(self.character)
        self.add_to_action_log(f'<{spell_result}>')
        await self.display_action_log()

        await interaction.response.defer()


    async def talk(self, interaction: discord.Interaction):
        if self.talking_to is None:
            await interaction.response.send_message("You are not talking to an NPC", ephemeral=True, delete_after=5)
            return

        # get the npc
        npc = self.talking_to

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
        await self.display_action_log()

        await interaction.response.defer()

    @tasks.loop(seconds=2)
    async def update_personal_embed(self):
        # update the embed
        embed = self.message.embeds[0]
        embed.set_field_at(1,
                           name="CURRENT LOCATION",
                           value=f"__{self.character.current_building.name}__ : {self.character.current_building.description}",
                           inline=True)

        npcs = self.character.current_building.get_present_npcs()
        npc_string = ""
        for npc in npcs:
            npc_string += f"- {npc.name} : {npc.description}\n"
        embed.set_field_at(2,
                           name="PRESENT NPCs",
                           value=npc_string,
                           inline=True)

        players = self.character.current_building.get_present_players()
        player_string = ""
        for player in players:
            player_string += f"- {player.name}\n"
        embed.set_field_at(3,
                           name="PRESENT PLAYERS",
                           value=player_string,
                           inline=True)

        # modify the message if it still exists (should happen only if the thread got deleted)
        try:
            await self.message.edit(embed=embed)
        except discord.errors.NotFound:
            pass

# =========================] MODALS [=========================
