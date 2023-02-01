import json
import discord
import character
import util
from settings import *
from discord.ext import commands

class Dnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog loaded successfully')

    #command to register a character
    @commands.command()
    async def register(self, ctx : discord.ext.commands.Context):
        if self.is_registered(ctx.author.id):
            await ctx.send("You are already registered")
            return

        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        #create a new discord thread
        thread = await ctx.channel.create_thread(name="Character creation", reason="Character creation", auto_archive_duration=60)
        await thread.send(f"{ctx.author.mention} is creating a new character")

        if not await self.new_character(thread, characters, ctx.author.id, ctx.author):
            await thread.send("Character creation failed")
            return

        with open(CHARACTER_FOLDER + 'characters.json', 'w') as f:
            json.dump(characters, f)

        await thread.delete()
        await ctx.send("You are now registered")

    @commands.command()
    async def unregister(self, ctx):
        if not self.is_registered(ctx.author.id):
            await ctx.send("You are not registered")
            return

        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        del characters[str(ctx.author.id)]

        with open(CHARACTER_FOLDER + 'characters.json', 'w') as f:
            json.dump(characters, f)

        await ctx.send("You are now unregistered")

    @commands.command()
    async def character(self, ctx):
        if not self.is_registered(ctx.author.id):
            await ctx.send("You are not registered")
            return

        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        #send character sheet in an embed
        embed = discord.Embed(title="Character sheet", description="Here is your character sheet", color=0x00ff00)
        embed.add_field(name="Name", value=characters[str(ctx.author.id)]["name"], inline=False)
        embed.add_field(name="Class", value=characters[str(ctx.author.id)]["class"], inline=False)
        embed.add_field(name="Gender", value=characters[str(ctx.author.id)]["gender"], inline=False)
        embed.add_field(name="Age", value=characters[str(ctx.author.id)]["age"], inline=False)
        await ctx.send(embed=embed)

    async def new_character(self, thread, characters, user_id, author):
        characters[user_id] = {}

        #character name
        res = await util.question(self.bot, thread, "What is your character's name?", str, author)
        if not res : return False
        characters[user_id]["name"] = res

        #character gender
        res = await util.question(self.bot, thread, "What is your character's gender?", str, author)
        if not res : return False
        characters[user_id]["gender"] = res

        #character class
        res = await util.choose(self.bot, thread, ["Warrior", "Mage", "Rogue"], author)
        if not res : return False
        characters[user_id]["class"] = res

        #character age
        res = await util.question(self.bot, thread, "What is your character's age?", int, author)
        if not res : return False
        characters[user_id]["age"] = res

        return characters


    #command to see if a character is registered
    def is_registered(self, user_id):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        return characters.get(str(user_id)) != None

async def setup(bot):
    await bot.add_cog(Dnd(bot))