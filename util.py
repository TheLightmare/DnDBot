import asyncio
import discord
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
    embed.add_field(name="POINTS LEFT", value="10", inline=False)
    embed.add_field(name="===================", value="", inline=False)
    embed.add_field(name="Strength", value="10", inline=False)
    embed.add_field(name="Dexterity", value="10", inline=False)
    embed.add_field(name="Constitution", value="10", inline=False)
    embed.add_field(name="Intelligence", value="10", inline=False)
    embed.add_field(name="Wisdom", value="10", inline=False)
    embed.add_field(name="Charisma", value="10", inline=False)

    await thread.send(embed = embed, view = dnd_ui.StatsDistributionUI(thread, character))



# function to load classes.json in a python list
def load_classes():
    with open(CONTENT_FOLDER + 'classes/classes.json', 'r') as f:
        classes = json.load(f)
    return classes["Classes"]


# function to load races.json in a python list
def load_races():
    with open(CONTENT_FOLDER + "races/races.json", 'r') as f:
        races = json.load(f)
    return races["Races"]

# function to load weapons.json in a python list
def load_weapons():
    with open(CONTENT_FOLDER + "items/weapons.json", 'r') as f:
        weapons = json.load(f)
        print(weapons)
    return weapons