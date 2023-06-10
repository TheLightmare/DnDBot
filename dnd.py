import json
import discord
import dnd_ui
import util
from settings import *
from discord.ext import commands
from discord.ui import Modal
from dnd_ui import *
from character import Character

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

        await util.create_character(self.bot, thread, ctx.author)



    @commands.command()
    async def unregister(self, ctx):
        if not self.is_registered(ctx.author.id):
            await ctx.send("You are not registered")
            return

        character = Character(ctx.author)
        character.load()

        # confirm deletion using buttons
        deleteconfirmUI = dnd_ui.DeleteCharacterUI(ctx.author, character)

        await ctx.send("Are you sure you want to delete your character?", view=deleteconfirmUI)



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
        embed.add_field(name="Race", value=characters[str(ctx.author.id)]["race"], inline=False)
        embed.add_field(name="Class", value=characters[str(ctx.author.id)]["class"], inline=False)
        embed.add_field(name="Gender", value=characters[str(ctx.author.id)]["gender"], inline=False)
        embed.add_field(name="Age", value=characters[str(ctx.author.id)]["age"], inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def test_stats(self, ctx):
        stats = await util.create_character(self.bot, ctx.channel, ctx.author.id)


    #command to see if a character is registered
    def is_registered(self, user_id):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        character = characters.get(str(user_id))
        return character


async def setup(bot):
    await bot.add_cog(Dnd(bot))