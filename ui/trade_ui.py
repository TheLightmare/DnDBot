import discord
from discord import SelectOption
from discord.ext import commands, tasks
from discord.ui import Button, View, Select, UserSelect, Modal, TextInput
import json
from util.item import *

class TradeUI(View):
    def __init__(self, player, character, npc, player_ui):
        super().__init__()

        self.player = player
        self.character = character
        self.npc = npc
        self.player_ui = player_ui

        # current selected items to buy
        self.buy_items = []
        # current selected items to sell
        self.sell_items = []

        # create the buttons
        self.buy_button = Button(
            style=discord.ButtonStyle.green,
            label="Buy",
        )
        self.buy_button.callback = self.buy

        self.sell_button = Button(
            style=discord.ButtonStyle.red,
            label="Sell",
        )
        self.sell_button.callback = self.sell

        self.exit_button = Button(
            style=discord.ButtonStyle.grey,
            label="Exit",
        )
        self.exit_button.callback = self.exit

        # scroll menu for buying
        self.buy_options = []
        for item_id in self.npc.inventory:
            item = Item(item_id)
            item.load()
            self.buy_options.append(SelectOption(label=item.name, value=item.id))
        if self.buy_options == []:
            self.buy_options.append(SelectOption(label="This merchant has nothing to sell", value="none"))
        self.buy_menu = Select(
            placeholder="Select an item to buy",
            options=self.buy_options,
            min_values=1
        )
        self.buy_menu.callback = self.buy_select

        # scroll menu for selling
        self.sell_options = []
        for trade_good in self.character.inventory:
            (category, item_id) = trade_good.split(":", 1)
            if category == "item":
                item = Item(item_id)
                item.load()
            if category == "weapon":
                item = Weapon(item_id)
                item.load()
            self.sell_options.append(SelectOption(label=item.name, value=item.id))
        if self.sell_options == []:
            self.sell_options.append(SelectOption(label="You have nothing to sell", value="none"))
        self.sell_menu = Select(
            placeholder="Select an item to sell",
            options=self.sell_options,
            min_values=1
        )
        self.sell_menu.callback = self.sell_select

        # add the buttons to the view
        self.add_item(self.buy_button)
        self.add_item(self.sell_button)
        self.add_item(self.exit_button)

        # add the menus to the view
        self.add_item(self.buy_menu)
        self.add_item(self.sell_menu)


    async def buy(self, interaction: discord.Interaction):
        # check if items are selected
        if self.buy_items == []:
            await interaction.response.send_message("You have not selected any items to buy.", ephemeral=True, delete_after=5)
            return

        # check if player has enough gold
        total_cost = 0
        for item in self.buy_items:
            total_cost += item.value
        if self.character.gold < total_cost:
            await interaction.response.send_message("You do not have enough gold to buy these items.", ephemeral=True, delete_after=5)
            return

        # remove gold from player
        self.character.gold -= total_cost

        # add items to player inventory
        for item in self.buy_items:
            self.character.inventory.append(item.id)
            self.character.save()

        # remove items from npc inventory
        for item in self.buy_items:
            self.npc.inventory.remove(item.id)

        # clear the buy items
        self.buy_items = []

        await interaction.response.defer()

    async def sell(self, interaction: discord.Interaction):
        # check if items are selected
        if self.sell_items == []:
            await interaction.response.send_message("You have not selected any items to sell.", ephemeral=True, delete_after=5)
            return

        # remove items from player inventory
        for item in self.sell_items:
            self.character.inventory.remove(item)
            self.character.save()

        # add items to npc inventory
        for item in self.sell_items:
            self.npc.inventory.append(item)

        # add gold to player
        total_cost = 0
        for item in self.sell_items:
            total_cost += item.value
        self.character.gold += total_cost

        # clear the sell items
        self.sell_items = []

        await interaction.response.defer()

    async def exit(self, interaction: discord.Interaction):
        # remove the trade message
        await interaction.response.defer()
        await interaction.delete_original_response()

    async def buy_select(self, interaction: discord.Interaction):
        # get the selected items
        self.buy_items = []
        for item_id in interaction.data["values"]:
            item = Item(item_id)
            item.load()
            self.buy_items.append(item)

        await interaction.response.defer()

    async def sell_select(self, interaction: discord.Interaction):
        # get the selected items
        self.sell_items = []
        for item in interaction.data["values"]:
            self.sell_items.append(Item.load(item))

        await interaction.response.defer()