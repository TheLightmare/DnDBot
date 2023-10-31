import json

import discord
from discord.ext import commands
from discord import app_commands

from util import misc_utils
from character import Character
from play import Play
from ui import character_ui
from util.settings import *


class Dnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Cog loaded successfully')

    #command to register a character
    @app_commands.command(name="register", description="Register a new character")
    async def register(self, interaction : discord.Interaction):
        if self.is_registered(interaction.user.id):
            await interaction.response.send_message("You are already registered")
            return

        await interaction.response.send_message("Starting character creation !", delete_after=5)

        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        #create a new discord thread
        thread = await interaction.channel.create_thread(name="Character creation", reason="Character creation", auto_archive_duration=60)
        await thread.send(f"{interaction.user.mention} is creating a new character")

        await misc_utils.create_character(self.bot, thread, interaction.user)



    @app_commands.command(name="unregister", description="Unregister your character")
    async def unregister(self, interaction : discord.Interaction):
        if not self.is_registered(interaction.user.id):
            await interaction.response.send_message("You are not registered")
            return

        character = Character(interaction.user)
        character.load()

        # confirm deletion using buttons
        deleteconfirmUI = character_ui.DeleteCharacterUI(interaction.user, character)

        await interaction.response.send_message("Are you sure you want to delete your character?", view=deleteconfirmUI)



    @app_commands.command(name="character", description="View your character sheet")
    async def character(self, interaction: discord.Interaction, user : discord.Member = None):
        if user is None:
            user = interaction.user
        if not self.is_registered(user.id):
            await interaction.response.send_message(f"{user.name} is not registered")
            return

        await misc_utils.character_sheet(self.bot, interaction.channel, user)
        await interaction.response.defer()


    @app_commands.command(name="host", description="Host a new DnD game")
    async def host(self, interaction : discord.Interaction):
        if not self.is_registered(interaction.user.id):
            await interaction.response.send_message("You are not registered", delete_after=5)
            return

        await interaction.response.send_message("Starting a new game ! Hold tight !", delete_after=5)

        character = Character(interaction.user)
        character.load()

        # create a new discord thread
        thread = await interaction.channel.create_thread(name=f"{interaction.user}'s Room", reason="DnD")
        await thread.send(f"{interaction.user.mention} is playing DnD")

        play = Play(self.bot, thread, interaction.user)
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