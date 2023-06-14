import util
from discord.ext import commands
from ui.character_ui import *
from character import Character
from ui import character_ui, dnd_ui
import json
import discord
from settings import *
import asyncio
from play import Play

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

        await ctx.send("Starting character creation !", delete_after=5, reference=ctx.message)

        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        #create a new discord thread
        thread = await ctx.channel.create_thread(name="Character creation", reason="Character creation", auto_archive_duration=60)
        await thread.send(f"{ctx.author.mention} is creating a new character")

        await util.create_character(self.bot, thread, ctx.author)



    @commands.command()
    async def unregister(self, ctx):
        if not self.is_registered(ctx.author.id):
            await ctx.send("You are not registered")
            return

        character = Character(ctx.author)
        character.load()

        # confirm deletion using buttons
        deleteconfirmUI = character_ui.DeleteCharacterUI(ctx.author, character)

        await ctx.send("Are you sure you want to delete your character?", view=deleteconfirmUI)



    @commands.command()
    async def character(self, ctx, user : discord.Member = None):
        if user is None:
            user = ctx.author
        if not self.is_registered(user.id):
            await ctx.send(f"{user.name} is not registered")
            return

        await util.character_sheet(self.bot, ctx.channel, user)


    @commands.command()
    async def play(self, ctx):
        if not self.is_registered(ctx.author.id):
            await ctx.send("You are not registered", delete_after=5, reference=ctx.message)
            return

        await ctx.send("Starting a new game ! Hold tight !", delete_after=5, reference=ctx.message)

        character = Character(ctx.author)
        character.load()

        # create a new discord thread
        thread = await ctx.channel.create_thread(name="DnD", reason="DnD")
        await thread.send(f"{ctx.author.mention} is playing DnD")

        play = Play(self.bot, thread, ctx.author)
        await play.start()


    def get_character(self, user_id):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        character = characters.get(str(user_id))
        return character

    def is_registered(self, user_id):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        return str(user_id) in characters


async def setup(bot):
    await bot.add_cog(Dnd(bot))