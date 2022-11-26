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


class Feedback(discord.ui.Modal, title="Feedback"):
    name = discord.ui.TextInput(
        label="Name",
        placeholder="Your name here...",
    )

    feedback = discord.ui.TextInput(
        label="What do you think of this new feature?",
        style=discord.TextStyle.long,
        placeholder="Type your feedback here...",
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Thanks for your feedback, {self.name.value}!", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )

        traceback.print_tb(error.__traceback__)


client = MyClient()


@client.tree.command(guild=TEST_GUILD, description="Submit feedback")
async def feedback(interaction: discord.Interaction):
    await interaction.response.send_modal(Feedback())


client.run(os.getenv("DISCORD_TOKEN"))
