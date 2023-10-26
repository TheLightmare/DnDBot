from discord.ui import Button, View, UserSelect
from util.misc_utils import *
from character import Character
from ui.campaign_ui import CampaignUI
from world.world import World


class LobbyUI(View):
    def __init__(self, bot, thread: discord.Thread, host: discord.Member, tasks: list = []):
        super().__init__(timeout=None)

        self.host = host
        self.bot = bot
        self.thread = thread
        self.tasks = tasks

        self.players = [self.host]
        character = Character(self.host)
        character.load()
        self.characters = [character]

        invite_player = UserSelect(
            placeholder="Add Player",
        )
        invite_player.callback = self.invite_player

        remove_player = UserSelect(
            placeholder="Remove Player",
        )
        remove_player.callback = self.remove_player

        START_CAMPAIGN = Button(
            label="Start Campaign",
            style=discord.ButtonStyle.green
        )
        START_CAMPAIGN.callback = self.start_campaign

        LEAVE = Button(
            label="Leave",
            style=discord.ButtonStyle.red
        )
        LEAVE.callback = self.leave

        self.add_item(invite_player)
        self.add_item(remove_player)
        self.add_item(START_CAMPAIGN)
        self.add_item(LEAVE)

        # background tasks
        self.tasks.append(player_chat.start(self.thread, self.players))


    async def invite_player(self, interaction: discord.Interaction):
        # check if the one who invited is the host
        if interaction.user != self.host:
            await interaction.response.send_message("You are not the host", ephemeral=True, delete_after=5)
            return

        player = interaction.data['values'][0]
        # make player into a discord.Member
        player = await self.bot.fetch_user(player)

        # check if the player is already in the game
        if player in self.players:
            await interaction.response.send_message(f"{player.name} is already in the game", ephemeral=True, delete_after=5)
            return
        if not self.is_registered(player.id):
            await interaction.response.send_message(f"{player.name} is not registered", ephemeral=True, delete_after=5)
            return
        self.players.append(player)
        character = Character(player)
        character.load()
        self.characters.append(character)

        # invite the player to the thread
        await self.thread.add_user(player)

        # send a message in the thread to the player
        await self.thread.send(f"{player.mention}, you have joined the game ! Wait for the host to send the Campaign UI, then click on the button to get your own interface !", delete_after=10)

        # update the embed
        embed = interaction.message.embeds[0]
        embed.set_field_at(1, name="Players", value=" ".join([player.mention for player in self.players]), inline=False)
        await interaction.message.edit(embed=embed)

        await interaction.response.defer()


    async def remove_player(self, interaction: discord.Interaction):
        # check if the one who invited is the host
        if interaction.user != self.host:
            await interaction.response.send_message("You are not the host", ephemeral=True, delete_after=5)
            return

        player = interaction.data['values'][0]
        # make player into a discord.Member
        player = await self.bot.fetch_user(player)

        # check if the player is self
        if player == interaction.user:
            await interaction.response.send_message("You cannot remove yourself ! Use the 'Leave' button for that !", ephemeral=True, delete_after=5)
            return

        # check if the player is already not in the game
        if player not in self.players:
            await interaction.response.send_message(f"{player.name} is not in the game", ephemeral=True, delete_after=5)
            return
        self.players.remove(player)

        self.characters.remove(self.get_character(player))

        # remove the player from the thread
        await self.thread.remove_user(player)

        await interaction.response.defer()


    async def start_campaign(self, interaction: discord.Interaction):
        # check if the one who invited is the host
        if interaction.user != self.host:
            await interaction.response.send_message("You are not the host", ephemeral=True, delete_after=5)
            return

        # create the embed
        embed = discord.Embed(title="Campaign UI", description="This is the campaign interface", color=0x00ff00)
        embed.add_field(name="CURRENT LOCATION", value="", inline=True)
        embed.add_field(name="CURRENT TIME", value="", inline=True)
        embed.add_field(name="CURRENT WEATHER", value="", inline=True)
        embed.add_field(name="CURRENT TEMPERATURE", value="", inline=True)

        embed.add_field(name="MAP OF SURROUNDINGS", value="", inline=False)

        # send the embed
        self.world = World()
        message = await self.thread.send(embed=embed, view=CampaignUI(self.bot, self.thread, self.players, self.host, self.characters, self.world))

        # start the background tasks
        self.tasks.append(update_campaign_embed.start(message, self.get_character(self.host), world=self.world))

        await interaction.response.defer()

    async def leave(self, interaction: discord.Interaction):
        # remove the player from the game
        self.players.remove(interaction.user)

        self.characters.remove(self.get_character(interaction.user))

        # remove the player from the thread
        await self.thread.remove_user(interaction.user)

        # send a message in the thread to the player
        await self.thread.send(f"{interaction.user} left the game !", delete_after=10)

        # check if no one is left
        if len(self.players) == 0:
            # delete the thread
            await self.thread.delete()
            # terminate the tasks
            for task in self.tasks:
                task.cancel()
            return

        # check if the host left
        if interaction.user == self.host:
            # make the first player the host
            self.host = self.players[0]
            # update the embed
            embed = interaction.message.embeds[0]
            embed.set_field_at(0, name="Host", value=self.host.mention, inline=False)
            await interaction.message.edit(embed=embed)
            # send a message in the thread to the player
            await self.thread.send(f"{self.host} is now the host !", delete_after=10)


    def is_registered(self, player_id):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)
        return str(player_id) in characters

    def get_character(self, player):
        for character in self.characters:
            if character.author == player:
                return character


@tasks.loop(seconds=2)
async def update_campaign_embed(message, host_character: Character, world: World):
    # update the embed
    embed = message.embeds[0]
    embed.set_field_at(0, name="CURRENT LOCATION", value=f"__{host_character.current_location.name}__ : {host_character.current_location.description}", inline=True)
    embed.set_field_at(1, name="CURRENT TIME", value=f"{world.time}", inline=True)

    # modify the message
    await message.edit(embed=embed)

@tasks.loop(seconds=1)
async def player_chat(thread: discord.Thread, players: list):
    messages = []
    async for message in thread.history():
        if message.author in players:
            messages.append(message)

            if len(messages) >= 6:
                msg = messages.pop()
                await msg.delete()