import asyncio
import discord
from discord.ext import tasks
import json
from character import Character
from util.settings import *
from ui import character_ui


# distribute character stats using an embed and buttons
async def create_character(bot, thread, author):
    # create a character object
    character = Character(author)

    # create character info embed
    embed = discord.Embed(title="Character info", description="Enter your character info", color=0x00ff00)
    embed.add_field(name="Name", value="*Enter a character name*", inline=False)
    embed.add_field(name="Age", value="*Enter character age*", inline=False)
    embed.add_field(name="Race", value="*Choose race*", inline=False)
    embed.add_field(name="Class", value="*Choose class*", inline=False)

    character_view = character_ui.CharacterCreationUI(character)
    await thread.send(embed = embed, view = character_view)
    while not character_view.finished:
        await asyncio.sleep(1)

    #create character equipment/spells embed
    embed = discord.Embed(title="Equipment", description="use the arrows to select the slot and then choose the item/spell", color=0x00ff00)
    embed.add_field(name="Equipment", value="*Choose equipment*", inline=False)

    await thread.send(embed = embed, view = character_ui.EquipmentUI(character))

    #create character spells embed
    embed = discord.Embed(title="Spells", description="choose the spells in the scroll menu and add them using the button", color=0x00ff00)

    for i in range(9):
        if character.spell_slots[i] != 0:
            embed.add_field(name=f"Level {i}", value="*Choose spells* **<===**", inline=False)
            value = ""
            for j in range(character.spell_slots[i]):
                value += f"- *Choose spell*\n"
            embed.set_field_at(i, name=f"Level {i}", value=value, inline=False)
    spells_message = await thread.send(embed = embed, view = character_ui.SpellsUI(character))


    # create stats embed
    embed = discord.Embed(title="Stat distribution", description="Distribute your stats", color=0x00ff00)
    embed.add_field(name="POINTS LEFT", value=str(character.unspent_points), inline=False)
    embed.add_field(name="===================", value="", inline=False)
    embed.add_field(name="Strength", value="10", inline=False)
    embed.add_field(name="Dexterity", value="10", inline=False)
    embed.add_field(name="Constitution", value="10", inline=False)
    embed.add_field(name="Intelligence", value="10", inline=False)
    embed.add_field(name="Wisdom", value="10", inline=False)
    embed.add_field(name="Charisma", value="10", inline=False)

    stat_message = await thread.send(embed = embed, view = character_ui.StatsDistributionUI(thread, character))
    await refresh_ui.start(bot, [stat_message, spells_message], character)


@tasks.loop(seconds=5)
async def refresh_ui(bot, messages, character):
    await load_modifiers_UI(bot, messages[0], character)
    #await load_spell_slots_UI(bot, messages[1], character)

async def load_modifiers_UI(bot, message, character):
    # get embed
    embed = message.embeds[0]

    # modify the embed
    embed.set_field_at(0, name="POINTS LEFT", value=str(character.unspent_points), inline=False)
    embed.set_field_at(2, name="Strength", value=f"{character.stats['strength']} ({character.get_modifier('strength')})", inline=False)
    embed.set_field_at(3, name="Dexterity", value=f"{character.stats['dexterity']} ({character.get_modifier('dexterity')})", inline=False)
    embed.set_field_at(4, name="Constitution", value=f"{character.stats['constitution']} ({character.get_modifier('constitution')})", inline=False)
    embed.set_field_at(5, name="Intelligence", value=f"{character.stats['intelligence']} ({character.get_modifier('intelligence')})", inline=False)
    embed.set_field_at(6, name="Wisdom", value=f"{character.stats['wisdom']} ({character.get_modifier('wisdom')})", inline=False)
    embed.set_field_at(7, name="Charisma", value=f"{character.stats['charisma']} ({character.get_modifier('charisma')})", inline=False)

    # send the embed
    await message.edit(embed=embed)


async def load_spell_slots_UI(bot, message, character):
    # get embed
    embed = message.embeds[0]
    embed.clear_fields()

    # modify the embed
    for i in range(9):
        if character.spell_slots[i] != 0:
            embed.add_field(name=f"Level {i}", value="*Choose spells*", inline=False)
            value = ""
            for j in range(character.spell_slots[i]):
                if j < len(character.spells[i]):
                    value += f"- {character.spells[i][j].name}\n"
                else:
                    value += f"- *Choose spell*\n"
            embed.set_field_at(i, name=f"Level {i}", value=value, inline=False)

    # send the embed
    await message.edit(embed=embed)


async def character_sheet(bot, thread, author: discord.Member):
    # create a character object
    character = Character(author)
    character.load()

    # create character sheet embed
    embed = discord.Embed(title="Character sheet", description=f"Here is {author.mention}'s character sheet", color=0x00ff00)
    embed.add_field(name="Name", value=character.name, inline=False)
    embed.add_field(name="Age", value=character.age, inline=False)
    embed.add_field(name="Race", value=character.race, inline=False)
    embed.add_field(name="Class", value=character.job, inline=False)

    # add stats
    embed.add_field(name="===================", value="", inline=False)
    embed.add_field(name="Strength", value=f"{character.stats['strength']} ({character.get_modifier('strength')})", inline=True)
    embed.add_field(name="Dexterity", value=f"{character.stats['dexterity']} ({character.get_modifier('dexterity')})", inline=True)
    embed.add_field(name="Constitution", value=f"{character.stats['constitution']} ({character.get_modifier('constitution')})", inline=True)
    embed.add_field(name="Intelligence", value=f"{character.stats['intelligence']} ({character.get_modifier('intelligence')})", inline=True)
    embed.add_field(name="Wisdom", value=f"{character.stats['wisdom']} ({character.get_modifier('wisdom')})", inline=True)
    embed.add_field(name="Charisma", value=f"{character.stats['charisma']} ({character.get_modifier('charisma')})", inline=True)

    embed.add_field(name="===================", value="", inline=False)

    # add equipment
    inventory = ""
    for item in character.inventory:
        inventory += f"- {item}\n"
    embed.add_field(name="Equipment", value=character.inventory, inline=True)

    # add spells
    spells = ""
    for tier in range(len(character.spells)):
        spells += f"__Level {tier} :__\n"
        for spell in character.spells[tier]:
            spells += f"- {spell.name}\n"
    embed.add_field(name="**Spells**", value=spells, inline=True)

    # send the embed
    await thread.send(embed = embed)


#


# function to load classes.json in a python list
def load_classes():
    with open(CONTENT_FOLDER + 'classes/classes.json', 'r') as f:
        classes = json.load(f)
    return classes


# function to load races.json in a python list
def load_races():
    with open(CONTENT_FOLDER + "races/races.json", 'r') as f:
        races = json.load(f)
    return races

# function to load weapons.json in a python list
def load_weapons():
    with open(CONTENT_FOLDER + "items/items.json", 'r') as f:
        weapons = json.load(f)
    # remove non-weapons
    for weapon in weapons:
        if not weapon["properties"]["equipable"] and weapon["properties"]["tier"] > 1:
            weapons.remove(weapon)

    print(weapons)
    return weapons

# function to load spells.json in a python list
def load_spells():
    with open(CONTENT_FOLDER + "spells/spells.json", 'r') as f:
        spells = json.load(f)
    return spells