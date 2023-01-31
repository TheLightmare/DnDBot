import json
import discord
import character
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
    async def register(self, ctx):
        if self.is_registered(ctx.author.id):
            await ctx.send("You are already registered")
            return

        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        await self.new_character(ctx, characters, ctx.author.id)

        with open(CHARACTER_FOLDER + 'characters.json', 'w') as f:
            json.dump(characters, f)

        await ctx.send("You are now registered")


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

    async def new_character(self, ctx, characters, user_id):
        characters[user_id] = {}

        #character name
        characters[user_id]["name"] = self.question(ctx, "What is your character's name?")

        #character gender
        characters[user_id]["gender"] = self.question(ctx, "What is your character's gender?")

        #character class
        characters[user_id]["class"] = self.question(ctx, "What is your character's class?")

        #character age
        characters[user_id]["age"] = self.question(ctx, "What is your character's age?")

        return characters


    #function to ask a question
    async def question(self, ctx, question):
        await ctx.send(question)
        message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
        if message == None:
            await ctx.send("You didn't enter anything")
            return
        return message.content

    #command to see if a character is registered
    def is_registered(self, user_id):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        return characters.get(str(user_id)) != None

async def setup(bot):
    await bot.add_cog(Dnd(bot))