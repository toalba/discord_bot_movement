# Clear all commands

# TODO sync commands only on special command where the bot has to be mentioned, also check owner id
import os

import discord
from discord import app_commands
from dotenv import load_dotenv


class MyClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        bot_owner = await client.fetch_user(int(os.getenv("BOT_OWNER")))
        await bot_owner.send("Bot commands cleared")

    async def setup_hook(self) -> None:
        print(f"Clear commands for {TEST_GUILD}")
        self.tree.clear_commands(guild=TEST_GUILD)

        print(f"Sync commands for {TEST_GUILD}")
        await self.tree.sync(guild=TEST_GUILD)
        # await self.tree.sync()


if __name__ == '__main__':
    load_dotenv()
    TEST_GUILD = discord.Object(int(os.getenv("TEST_GUILD")))
    client = MyClient()
    client.run(token=os.getenv("DISCORD_TOKEN"), reconnect=False)
