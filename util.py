import asyncio
import discord
import json
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