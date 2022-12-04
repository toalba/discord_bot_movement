import os

import discord
from discord import Interaction
from discord import SelectOption
from discord import TextChannel
from discord import Thread
from discord import VoiceChannel
from discord import app_commands
from discord.ui import Select
from discord.ui import View
from dotenv import load_dotenv

from python_bot.logger import Logger, LOG_MOVE, LOG_ADMIN

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


logger = Logger()
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


@client.tree.command(guild=TEST_GUILD, description="Move users into a voice channel")
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


@client.tree.command(guild=TEST_GUILD, description="Set log channel of specific type")
@app_commands.choices(log_type=[
    app_commands.Choice[str](name="Move", value=LOG_MOVE),
    app_commands.Choice[str](name="Admin", value=LOG_ADMIN),
])
async def set_log_channel(interaction: Interaction, log_type: app_commands.Choice[str],
                          log_channel: TextChannel | Thread):
    admin_log_channel = Logger.get_log_channel_admin(guild=interaction.guild)
    if admin_log_channel:
        c = client.get_channel(admin_log_channel.id)
        await c.send("Something was changed!")
    logger.set_log_channel(channel=log_channel, log_type=log_type.value, guild=interaction.guild)
    await log_channel.send(f"This channel is now the log channel for `{log_type.name}` commands", delete_after=60)
    await interaction.response.send_message(f"You have set the `{log_type.name}` log channel to #{log_channel}")


client.run(os.getenv("DISCORD_TOKEN"))
