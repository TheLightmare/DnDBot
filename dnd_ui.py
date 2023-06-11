import json
import asyncio
import discord
from settings import *
from discord.ui import Modal, Button, View, Select, TextInput
from discord.components import SelectOption
from settings import *


# preloads stuff into SelectOptions
def load_weapons(max_tier) -> list:
    weapons = {}
    with open(CONTENT_FOLDER + "items/" + "weapons.json", "r") as file:
        weapons = json.load(file)
    options = []
    for element in weapons:
        weapon = weapons[element]
        if weapon["tier"] <= max_tier:
            options.append(SelectOption(label=weapon["name"], value=weapon["name"], description=weapon["description"]))
    return options

def load_spells(max_level) -> list:
    spells = {}
    with open(CONTENT_FOLDER + "spells/" + "spells.json", "r") as file:
        spells = json.load(file)
    options = []
    for element in spells:
        spell = spells[element]
        if spell["level"] <= max_level:
            options.append(SelectOption(label=spell["name"], value=spell["name"], description=spell["description"]))
    return options

def load_races() -> list:
    races = {}
    with open(CONTENT_FOLDER + "races/" + "races.json", "r") as file:
        races = json.load(file)
    options = []
    for element in races:
        race = races[element]
        options.append(SelectOption(label=race["name"], value=race["name"], description=race["description"]))
    return options

def load_classes() -> list:
    classes = {}
    with open(CONTENT_FOLDER + "classes/" + "classes.json", "r") as file:
        classes = json.load(file)
    options = []
    for element in classes:
        class_ = classes[element]
        options.append(SelectOption(label=class_["name"], value=class_["name"], description=class_["description"]))
    return options




# made this crap because Discord API does not let me use TextInputs in Views
class CharacterCreationModal(Modal):
    def __init__(self, character) -> None:
        super().__init__(title="Character Creation")
        self.character = character
        self.add_item(TextInput(label="What is your character's name ?", placeholder="Name", min_length=1, max_length=20, required=True))
        self.add_item(TextInput(label="What is your character's age ?", placeholder="Age", min_length=1, max_length=3, required=True))

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        #get embed
        embed = interaction.message.embeds[0]
        #modify embed
        self.name = self.children[0].value
        self.age = self.children[1].value
        self.character.name = self.name
        self.character.age = self.age
        embed.set_field_at(0, name="Name", value=self.name, inline=False)
        embed.set_field_at(1, name="Age", value=self.age, inline=False)
        #send embed
        await interaction.message.edit(embed=embed)
        await interaction.response.defer()



#view  to confirm character deletion
class DeleteCharacterUI(View):
    def __init__(self, author, character) -> None:
        super().__init__(timeout=None)
        self.author = author
        self.character = character

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.author.id

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message("Character deletion cancelled", ephemeral=True)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.character.delete()
        await interaction.message.delete()
        await interaction.response.send_message("Character deleted", ephemeral=True)


# atrocity
class CharacterCreationUI(View):
    def __init__(self, character) -> None:
        super().__init__(timeout=None)
        self.character = character


    # racism moment
    @discord.ui.select(options=load_races(), placeholder="Choose a race")
    async def race_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        #get embed
        embed = interaction.message.embeds[0]
        #modify embed
        embed.set_field_at(2, name="Race", value=select.values[0], inline=False)
        self.character.set_race(select.values[0])
        #send embed
        await interaction.message.edit(embed=embed)

        await interaction.response.defer()

    @discord.ui.select(options=load_classes(), placeholder="Choose a class")
    async def class_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        #get embed
        embed = interaction.message.embeds[0]
        #modify embed
        embed.set_field_at(3, name="Class", value=select.values[0], inline=False)
        self.character.job = select.values[0]
        #send embed
        await interaction.message.edit(embed=embed)

        await interaction.response.defer()

    @discord.ui.button(label="Edit Name and Age", style=discord.ButtonStyle.blurple)
    async def create_character(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CharacterCreationModal(self.character)
        await interaction.response.send_modal(modal)


class EquipmentUI(View):
    def __init__(self, character) -> None:
        super().__init__(timeout=None)
        self.character = character
        self.selected_equipment = None

    @discord.ui.select(options=load_weapons(1), placeholder="Choose a piece of equipment")
    async def equipmentselect(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_equipment = select.values[0]

        await interaction.response.defer()

    @discord.ui.button(label="Add Equipment", style=discord.ButtonStyle.blurple)
    async def addequipment(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.selected_equipment is None:
            await interaction.response.send_message("Please select a piece of equipment", ephemeral=True, delete_after=5)
            return

        #get embed
        embed = interaction.message.embeds[0]
        #modify embed
        embed.set_field_at(0, name="Equipment", value=self.selected_equipment, inline=False)
        self.character.inventory.append(self.selected_equipment)
        #send embed
        await interaction.message.edit(embed=embed)

        await interaction.response.defer()


class SpellsUI(View):
    def __init__(self, character) -> None:
        super().__init__(timeout=None)
        self.character = character
        self.selected_spell = None
        self.current_spells = ""

    @discord.ui.select(options=load_spells(1), placeholder="Choose a spell")
    async def spellselect(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_spell = select.values[0]
        await interaction.response.defer()

    @discord.ui.button(label="Add Spell", style=discord.ButtonStyle.blurple)
    async def addspell(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.selected_spell is None:
            await interaction.response.send_message("Please select a spell", ephemeral=True, delete_after=5)
            return

        #get embed
        embed = interaction.message.embeds[0]
        #modify embed
        self.current_spells += "- " + self.selected_spell + "\n"
        embed.set_field_at(0, name="Spells", value=self.current_spells, inline=False)
        self.character.spells.append(self.selected_spell)
        #send embed
        await interaction.message.edit(embed=embed)

        await interaction.response.defer()


# decent work
class StatsDistributionUI(View):
    def __init__(self, thread, character) -> None:
        super().__init__(timeout=None)
        self.current_stat = None
        self.thread = thread
        self.character = character

    @discord.ui.select(options=[discord.SelectOption(label="Strength", value="strength"),
                        discord.SelectOption(label="Dexterity", value="dexterity"),
                        discord.SelectOption(label="Constitution", value="constitution"),
                        discord.SelectOption(label="Intelligence", value="intelligence"),
                        discord.SelectOption(label="Wisdom", value="wisdom"),
                        discord.SelectOption(label="Charisma", value="charisma")],
                       placeholder="Choose stat to edit")
    async def statselect(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.current_stat = select.values[0]
        await interaction.response.defer()

    @discord.ui.button(label="Decrease", style=discord.ButtonStyle.red)
    async def decrease(self, interaction: discord.Interaction, button: discord.ui.Button):
        # get message embed
        embed = interaction.message.embeds[0]
        # get message content
        content = interaction.message.content

        # get the stat that the user wants to decrease
        stat = self.current_stat
        # get the value of the stat and the field
        value = self.character.stats[stat]
        selected_field = None
        for field in embed.fields:
            if field.name.lower() == stat:
                selected_field = field
                break
        # decrease the value of the stat
        if value > 0:
            value -= 1
            self.character.unspent_points += 1
        # update the embed
        modifier = self.character.stat_modifiers[stat]["race"]
        embed.set_field_at(embed.fields.index(selected_field), name=stat, value=f"{str(value)} ({modifier})", inline=False)
        embed.set_field_at(0, name="POINTS LEFT", value=str(self.character.unspent_points), inline=False)
        self.character.stats[stat] = value


        await interaction.message.edit(content=content, embed=embed)
        await interaction.response.defer()



    @discord.ui.button(label="Increase", style=discord.ButtonStyle.blurple)
    async def increase(self, interaction: discord.Interaction, button: discord.ui.Button):
        # get message embed
        embed = interaction.message.embeds[0]
        # get message content
        content = interaction.message.content

        # get the stat that the user wants to decrease
        stat = self.current_stat
        # get the value of the stat and the field
        value = self.character.stats[stat]
        selected_field = None
        for field in embed.fields:
            if field.name.lower() == stat:
                selected_field = field
                break
        # decrease the value of the stat
        if value < 20 and self.character.unspent_points > 0:
            value += 1
            self.character.unspent_points -= 1
        # update the embed

        modifier = self.character.stat_modifiers[stat]["race"]
        embed.set_field_at(embed.fields.index(selected_field), name=stat, value=f"{str(value)} ({modifier})", inline=False)
        embed.set_field_at(0, name="POINTS LEFT", value=str(self.character.unspent_points), inline=False)
        self.character.stats[stat] = value

        await interaction.message.edit(content=content, embed=embed)
        await interaction.response.defer()


    # pointless button, looks cool
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        # save the character
        self.character.save()

        # send blank response
        await interaction.response.defer()

        # delete the thread
        await self.thread.delete()


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        # send blank response
        await interaction.response.defer()

        # delete the thread
        await self.thread.delete()



