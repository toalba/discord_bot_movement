import os
import discord
from discord import app_commands
from discord.ui import Select
from discord.ui import View
from discord import SelectOption
from discord import Interaction
from discord import VoiceChannel
from dotenv import load_dotenv

load_dotenv()

TEST_GUILD = discord.Object(int(os.getenv("TEST_GUILD")))


class MyClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=TEST_GUILD)


client = MyClient()


class UserSelect(Select):
    def __init__(self, source_channel=None, destination_channel=None):
        self.source_channel = source_channel
        self.destination_channel = destination_channel
        self.members = self.source_channel.members
        opt = [
            SelectOption(label=member.display_name, value=member.id)
            for member in self.members
        ]
        super().__init__(
            placeholder="Select a user", min_values=1, max_values=len(opt), options=opt
        )

    async def callback(self, interaction: Interaction):
        for value in self.values:
            member = self.source_channel.guild.get_member(int(value))
            await member.move_to(self.destination_channel)
        await interaction.response.send_message(
            "Moved users", ephemeral=True, delete_after=60
        )


class SelectUserView(View):
    def __init__(self, source_channel, destination_channel):
        super().__init__()
        self.source_channel = source_channel
        self.destination_channel = destination_channel
        self.add_item(
            UserSelect(
                source_channel=source_channel, destination_channel=destination_channel
            )
        )


@client.tree.command(guild=TEST_GUILD, description="Move user into a voice channel")
@app_commands.checks.has_permissions(move_members=True)
async def mass_move_channel(
    interaction: Interaction,
    source_channel: VoiceChannel,
    destination_channel: VoiceChannel,
):
    source_channel_members = source_channel.members
    for member in source_channel_members:
        await member.move_to(destination_channel)
    await interaction.response.send_message(
        f"Moved {len(source_channel_members)} users from {source_channel.mention} to {destination_channel.mention}",
        delete_after=60,
        ephemeral=True,
    )

@mass_move_channel.error
async def mass_move_channel_error(interaction: Interaction, error: Exception):
    await interaction.response.send_message(
        f"Move action cancelled: You do not have the required permissions", ephemeral=True, delete_after=60
    )

@client.tree.command(guild=TEST_GUILD, description="Move user into a voice channel")
@app_commands.checks.has_permissions(move_members=True)
async def move_select_user(
    interaction: Interaction,
    source_channel: VoiceChannel,
    destination_channel: VoiceChannel,
):
    if len(source_channel.members) == 0:
        await interaction.response.send_message(
            "Move action cancelled: Source channel has no members",
            ephemeral=True,
            delete_after=60,
        )
        return

    await interaction.response.send_message(
        "Select a user to move",
        view=SelectUserView(source_channel, destination_channel),
        ephemeral=True,
        delete_after=60,
    )

@move_select_user.error
async def move_select_user_error(interaction, error):
    if isinstance(error, app_commands.errors.CheckFailure):
        await interaction.response.send_message(
            "Move action cancelled: You do not have the required permissions",
            ephemeral=True,
            delete_after=60,
        )


client.run(os.getenv("DISCORD_TOKEN"))
