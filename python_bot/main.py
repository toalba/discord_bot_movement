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


class Move(app_commands.Group):
    log_type = LOG_MOVE

    @app_commands.command(name="all", description="Move **all** users from one voice channel to another")
    @app_commands.describe(source_channel="Move users from this channel")
    @app_commands.describe(destination_channel="Move users to this channel")
    @app_commands.checks.has_permissions(move_members=True)
    async def move_all(self,
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
        log_channel = client.get_channel(
            client.logger.get_log_channel(interaction.guild, command_type=self.log_type).id)
        await log_channel.send(
            content=f"{interaction.user.mention} has moved {len(source_channel_members)} users "
                    f"from {source_channel.mention} to {destination_channel.mention}",
            allowed_mentions=discord.AllowedMentions(users=False))

    @app_commands.command(name="users", description="Move **1+** users into another voice channel")
    @app_commands.checks.has_permissions(move_members=True)
    async def move_users(self,
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

    @move_users.error
    async def move_users_error(self, interaction, error: Exception):
        if isinstance(error, app_commands.errors.CheckFailure):
            await interaction.response.send_message(
                "Move action cancelled: You do not have the required permissions",
                ephemeral=True,
                delete_after=60,
            )

    @move_all.error
    async def move_all_error(self, interaction: Interaction, error: Exception):
        await interaction.response.send_message(
            f"Move action cancelled: You do not have the required permissions\n{error}",
            ephemeral=True,
            delete_after=60
        )


class Settings(app_commands.Group):
    log_type = LOG_ADMIN

    @app_commands.command()
    @app_commands.describe(scope="category of logged events",
                           channel="target channel or thread")
    @app_commands.choices(scope=[
        app_commands.Choice(name="Move", value=LOG_MOVE),
        app_commands.Choice(name="Admin", value=LOG_ADMIN),
    ])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def log_channel(self, interaction: Interaction, scope: app_commands.Choice[str],
                          channel: TextChannel | Thread):
        admin_log_channel = Logger.get_log_channel(guild=interaction.guild, command_type=self.log_type)
        print(f"interaction.data.values: {interaction.data.values()}")
        if admin_log_channel:
            c = client.get_channel(admin_log_channel.id)
            await c.send("Something was changed!")
        client.logger.set_log_channel(channel=channel, command_type=scope.value, guild=interaction.guild)
        await channel.send(f"This channel is now the log channel for `{scope.name}` commands", delete_after=60)
        await interaction.response.send_message(f"You have set the `{scope.name}` log channel to #{channel}")



client.run(os.getenv("DISCORD_TOKEN"))
