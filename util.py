import asyncio
import discord
from discord.ext import tasks
from discord.ui import Button, View, Select
from discord.components import SelectOption
import dnd_ui
import json
from character import Character
from settings import *


# function to ask a question
async def question(bot, thread, question, type, author):
    answered = False
    while not answered:
        await thread.send(question)
        try :
            message = await bot.wait_for('message', check=lambda message: message.author == author, timeout=30)
        except asyncio.TimeoutError:
            await thread.send("You didn't answer in time")
            return False


        if message.content.isdigit() and type == int:
            answered = True
            return int(message.content)
        if message.content.isdigit() and not type == int:
            await thread.send("You didn't enter a valid string")

        if message.content.isalpha() and type == str:
            answered = True
            return message.content
        if message.content.isalpha() and not type == str:
            await thread.send("You didn't enter a valid number")


# function to choose in a list of options using reactions
async def choose(bot, thread, options, option_type, author):
    # create a list of emojis
    emojis = []
    for i in range(1, len(options) + 1):
        emojis.append(str(i) + "️⃣")

    text = f"Choose one of the {option_type} below"
    i = 0
    for option in options:
        text += f"\n{emojis[i]} {option}"
        i += 1

    # send the message with the options
    message = await thread.send(text)
    for i in range(len(options)):
        await message.add_reaction(emojis[i])

    # wait for the user to react and check if it is a valid reaction
    try :
        reaction, user = await bot.wait_for('reaction_add', check=lambda reaction, user: user == author and reaction.emoji in emojis, timeout=30)
    except asyncio.TimeoutError:
        await thread.send("You didn't answer in time")
        return False

    await thread.send(f"You chose {options[emojis.index(reaction.emoji)]}")

    # return the option that the user chose
    return options[emojis.index(reaction.emoji)]


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

    await thread.send(embed = embed, view = dnd_ui.CharacterCreationUI(character))

    #create character equipment/spells embed
    embed = discord.Embed(title="Equipment", description="use the arrows to select the slot and then choose the item/spell", color=0x00ff00)
    embed.add_field(name="Equipment", value="*Choose equipment*", inline=False)

    await thread.send(embed = embed, view = dnd_ui.EquipmentUI(character))

    #create character spells embed
    embed = discord.Embed(title="Spells", description="choose the spells in the scroll menu and add them using the button", color=0x00ff00)
    embed.add_field(name="Spells", value="*Choose spells*", inline=False)

    await thread.send(embed = embed, view = dnd_ui.SpellsUI(character))

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

    stat_message = await thread.send(embed = embed, view = dnd_ui.StatsDistributionUI(thread, character))
    await load_modifiers_UI.start(bot, stat_message, character)


@tasks.loop(seconds=5)
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
    embed.add_field(name="Strength", value=f"{character.stats['strength']} ({character.get_modifier('strength')})", inline=False)
    embed.add_field(name="Dexterity", value=f"{character.stats['dexterity']} ({character.get_modifier('dexterity')})", inline=False)
    embed.add_field(name="Constitution", value=f"{character.stats['constitution']} ({character.get_modifier('constitution')})", inline=False)
    embed.add_field(name="Intelligence", value=f"{character.stats['intelligence']} ({character.get_modifier('intelligence')})", inline=False)
    embed.add_field(name="Wisdom", value=f"{character.stats['wisdom']} ({character.get_modifier('wisdom')})", inline=False)
    embed.add_field(name="Charisma", value=f"{character.stats['charisma']} ({character.get_modifier('charisma')})", inline=False)

    # add equipment
    embed.add_field(name="===================", value="", inline=False)
    inventory = ""
    for item in character.inventory:
        inventory += f"- {item}\n"
    embed.add_field(name="Equipment", value=character.inventory, inline=False)

    # add spells
    embed.add_field(name="===================", value="", inline=False)
    spells = ""
    for spell in character.spells:
        spells += f"- {spell}\n"
    embed.add_field(name="Spells", value=spells, inline=False)

    # send the embed
    await thread.send(embed = embed)



#


# function to load classes.json in a python list
def load_classes():
    with open(CONTENT_FOLDER + 'classes/classes.json', 'r') as f:
        classes = json.load(f)
    return classes["Classes"]


# function to load races.json in a python list
def load_races():
    with open(CONTENT_FOLDER + "races/races.json", 'r') as f:
        races = json.load(f)
    return races

# function to load weapons.json in a python list
def load_weapons():
    with open(CONTENT_FOLDER + "items/weapons.json", 'r') as f:
        weapons = json.load(f)
        print(weapons)
    return weapons