import datetime
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
from sqlalchemy.exc import NoResultFound

import data.init_db as init_db
import python_bot.data.db_session as db_session
import python_bot.data.models as models
from python_bot.logger import Logger, LOG_MOVE, LOG_ADMIN

load_dotenv()

# semantic versioning
BOT_VERSION_MAJOR = 1  # Breaking changes, may require backup or reset of database
BOT_VERSION_MINOR = 0  # New features or significant changes, but still compatible with db
BOT_VERSION_PATCH = 0  # Bug fixes, no changes in functionality or interfaces
BOT_VERSION_IDENT = "beta.1"  # Identifier for development and testing builds

TEST_GUILD = discord.Object(int(os.getenv("TEST_GUILD")))


class MyClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)
        self.logger = Logger()

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        init_db.main("config.sqlite")
        await update_guild_db()

    async def setup_hook(self) -> None:
        await self.tree.sync()
        # await self.tree.sync(guild=TEST_GUILD)


async def update_guild_db():
    """iterate guilds, where the bot is a member and update or add them to the database"""
    for g in client.guilds:
        session = db_session.create_session()
        try:
            row: models.Guild = session.query(models.Guild).filter_by(id=g.id).one()
            row.name = g.name
            row.updated_at = datetime.datetime.now()
        except NoResultFound:
            owner = await client.fetch_user(g.owner_id)
            session.add(models.Guild(id=g.id, name=g.name, owner=owner.display_name))
        finally:
            session.commit()
            print(f"{len(client.guilds)} guilds updated")


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
            placeholder="Select one or more users", min_values=1, max_values=len(opt), options=opt
        )

    async def callback(self, interaction: Interaction):
        for value in self.values:
            member = self.source_channel.guild.get_member(int(value))
            await member.move_to(self.destination_channel)
        await interaction.response.send_message(
            f"Moved {len(self.values)} users from {self.source_channel.mention} to {self.destination_channel.mention}",
            ephemeral=True, delete_after=60
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

    @staticmethod
    def _get_voice_channel_from_interaction(interaction: Interaction) -> VoiceChannel | discord.StageChannel | None:
        try:
            res = interaction.guild.get_member(interaction.user.id).voice.channel
            return res
        except AttributeError:
            return None

    @staticmethod
    async def __send_error_message_no_source_channel(interaction: Interaction):
        await interaction.response.send_message(
            "Error: You need to provide a source channel if you are not in a voice channel",
            ephemeral=True,
            delete_after=60)

    @app_commands.command(name="all", description="Move all users from one voice channel to another")
    @app_commands.checks.has_permissions(move_members=True)
    @app_commands.describe(destination_channel="Move users to this channel")
    @app_commands.describe(source_channel="Move users from this channel "
                                          "(leave empty to move from your current channel)")
    @app_commands.rename(destination_channel="to", source_channel="from")
    async def move_all(self,
                       interaction: Interaction,
                       destination_channel: VoiceChannel,
                       source_channel: VoiceChannel = None,
                       ):
        if not source_channel:
            source_channel = Move._get_voice_channel_from_interaction(interaction)
            if not source_channel:
                await Move.__send_error_message_no_source_channel(interaction)
                return
        source_channel_members = source_channel.members
        for member in source_channel_members:
            await member.move_to(channel=destination_channel,
                                 reason=f"Moved by {interaction.user.display_name}")
        await interaction.response.send_message(
            f"Moved {len(source_channel_members)} users from {source_channel.mention} to {destination_channel.mention}",
            delete_after=60,
            ephemeral=True,
        )
        log_channel = client.get_channel(
            client.logger.get_log_channel(guild=discord.Object(interaction.guild.id),
                                          command_type=self.log_type).id)
        await log_channel.send(
            content=f"{interaction.user.mention} has moved {len(source_channel_members)} users "
                    f"from {source_channel.mention} to {destination_channel.mention}",
            allowed_mentions=discord.AllowedMentions(users=False))

    @app_commands.command(name="users", description="Move 1+ users into another voice channel")
    @app_commands.checks.has_permissions(move_members=True)
    @app_commands.describe(destination_channel="Move users to this channel")
    @app_commands.describe(source_channel="Move users from this channel "
                                          "(leave empty to move from your current channel)")
    @app_commands.rename(destination_channel="to", source_channel="from")
    async def move_users(self,
                         interaction: Interaction,
                         destination_channel: VoiceChannel,
                         source_channel: VoiceChannel = None,
                         ):
        if not source_channel:
            source_channel = Move._get_voice_channel_from_interaction(interaction)
            if not source_channel:
                await Move.__send_error_message_no_source_channel(interaction)
                return

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
        log_channel = client.get_channel(
            client.logger.get_log_channel(guild=discord.Object(interaction.guild.id),
                                          command_type=self.log_type).id)
        await log_channel.send(
            content=f"{interaction.user.mention} has moved users by manual selection "
                    f"from {source_channel.mention} to {destination_channel.mention}",
            allowed_mentions=discord.AllowedMentions(users=False))

    @move_users.error
    async def move_users_error(self, interaction, error: Exception):
        if isinstance(error, app_commands.errors.CheckFailure):
            await interaction.response.send_message(
                f"`Move users` action cancelled: You do not have the required permissions\n{error}",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(f"An error has occurred: {error}")

    @move_all.error
    async def move_all_error(self, interaction: Interaction, error: Exception):
        if isinstance(error, AttributeError):
            await interaction.response.send_message(f"{error}")
            return
        await interaction.response.send_message(
            f"`Move all` action cancelled: You do not have the required permissions\n{error}",
            ephemeral=True,
        )


class Settings(app_commands.Group):
    log_type = LOG_ADMIN

    @app_commands.command(name="log_channel", description="Set target channel for a group of loggable events")
    @app_commands.describe(scope="category of logged events",
                           channel="target channel or thread")
    @app_commands.choices(scope=[
        app_commands.Choice(name="Move", value=LOG_MOVE),
        app_commands.Choice(name="Admin", value=LOG_ADMIN),
    ])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def log_channel(self, interaction: Interaction, scope: app_commands.Choice[str],
                          channel: TextChannel | Thread):
        admin_log_channel = Logger.get_log_channel(guild=discord.Object(interaction.guild.id),
                                                   command_type=self.log_type)
        try:
            if admin_log_channel:
                c = client.get_channel(admin_log_channel.id)
                await c.send(
                    f"{interaction.user.mention} has changed {scope.name}-Log channel to {channel.mention}",
                    allowed_mentions=discord.AllowedMentions(users=False))
            client.logger.set_log_channel(channel=channel, command_type=scope.value, guild=interaction.guild)
            await channel.send(f"This channel is now the log channel for `{scope.name}` commands", delete_after=60)
            await interaction.response.send_message(
                f"You have set the `{scope.name}` log channel to #{channel.mention}")
        except discord.Forbidden as e:
            app_permissions = interaction.app_permissions
            permissions = {
                "send_messages": app_permissions.send_messages,
                "send_tts_messages": app_permissions.send_tts_messages,
            }
            await interaction.response.send_message(
                f"Missing permissions: {e.text}\nMy permissions are {permissions}")


@client.tree.command(guild=TEST_GUILD, description="Get bot version info")
async def version(interaction: Interaction):
    version_str = f"`v{BOT_VERSION_MAJOR}.{BOT_VERSION_MINOR}.{BOT_VERSION_PATCH}" \
                  f"{'-' + BOT_VERSION_IDENT if BOT_VERSION_IDENT else ''}`"
    await interaction.response.send_message(version_str, ephemeral=True)


client.tree.add_command(Settings(), guild=TEST_GUILD)
client.tree.add_command(Move(), guild=TEST_GUILD)

client.run(os.getenv("DISCORD_TOKEN"))
