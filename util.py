import asyncio
import discord
from settings import *


# function to ask a question
async def question(bot, thread, question, type, author):
    answered = False
    while not answered:
        await thread.send(question)
        try :
            message = await bot.wait_for('message', check=lambda message: message.author == author, timeout=10)
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
async def choose(bot, thread, options, author):
    # create a list of emojis
    emojis = []
    for i in range(1, len(options) + 1):
        emojis.append(str(i) + "️⃣")

    text = "Choose one of the options below"
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
        reaction, user = await bot.wait_for('reaction_add', check=lambda reaction, user: user == author and reaction.emoji in emojis, timeout=10)
    except asyncio.TimeoutError:
        await thread.send("You didn't answer in time")
        return False

    await thread.send(f"You chose {options[emojis.index(reaction.emoji)]}")

    # return the option that the user chose
    return options[emojis.index(reaction.emoji)]