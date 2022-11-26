import os
import discord
from discord import app_commands

from dotenv import load_dotenv

import traceback

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

class UserSelect(discord.ui.Select):

    def __init__(self,source_channel=None,destination_channel=None):
        self.source_channel = source_channel
        self.destination_channel = destination_channel
        self.members = self.source_channel.members
        # When there is nobody in source channel..... 
        opt = [discord.SelectOption(label=member.display_name,value=member.id) for member in self.members]
        super().__init__(placeholder="Select a user", min_values=1, max_values=len(opt), options=opt)
    
    async def callback(self, interaction: discord.Interaction):
        for value in self.values:
            member = self.source_channel.guild.get_member(int(value))
            await member.move_to(self.destination_channel)
        await interaction.response.send_message("Moved users", ephemeral=True)

class SelectUserView(discord.ui.View):
    def __init__(self,source_channel,destination_channel):
        super().__init__()
        self.source_channel = source_channel
        self.destination_channel = destination_channel
        self.add_item(UserSelect(source_channel=source_channel,destination_channel=destination_channel))

    

@client.tree.command(guild=TEST_GUILD, description="Move user into a voice channel")
async def mass_move_channel(interaction: discord.Interaction, source_channel: discord.VoiceChannel, destination_channel: discord.VoiceChannel):
    source_channel_members = source_channel.members
    for member in source_channel_members:
        await member.move_to(destination_channel)
    await interaction.response.send_message(f"Moved {len(source_channel_members)} users from {source_channel.mention} to {destination_channel.mention}")

@client.tree.command(guild=TEST_GUILD, description="Move user into a voice channel")
async def move_select_user(interaction: discord.Interaction, source_channel: discord.VoiceChannel, destination_channel: discord.VoiceChannel):
    await interaction.response.send_message("Select a user to move", view=SelectUserView(source_channel,destination_channel),ephemeral=True)


client.run(os.getenv("DISCORD_TOKEN"))
