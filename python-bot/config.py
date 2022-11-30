import discord
import json


class ConfigMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwds):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwds)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=ConfigMeta):
    guilds = dict()

    def read_config(self):
        # TODO guard(file does not exist)
        with open("./config/guilds.json", "r") as read_file:
            self.guilds: dict = json.load(read_file)

    def write_config(self):
        with open("./config/config2.json", "w") as write_file:
            json.dump(self.guilds, write_file)

    def get_guild_log_channel(self, guild_query: discord.Object) -> discord.Object:
        res = None
        for guild in self.guilds.get("guilds").get("guild"):
            guild_id = int(guild.get("id"))
            if guild_id == guild_query.id:
                log_channel_id = guild.get("config").get("log_channel")
                res = discord.Object(log_channel_id)
        return res

    def _add_guild(self, guild: discord.Object) -> None:
        pass

    def set_guild_log_channel(self, guild_query: discord.Object) -> None:
        # TODO guard(guild does not exist) -> _add_guild(guild_query.id)
        # TODO set or update log_channel value
        pass


if __name__ == "__main__":
    print("Module: 'config.py'")
