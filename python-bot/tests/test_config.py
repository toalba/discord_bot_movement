import discord
import pytest

from config import Config


TEST_CONFIG_PATH = "python-bot/config/guilds.json.sample"


def test_invalid_config_path() -> None:
    conf = Config("./invalidpath")
    with pytest.raises(FileNotFoundError):
        conf.read_config()
    del conf


def test_sample_config() -> None:
    # test example file with expected data structure
    conf = Config(TEST_CONFIG_PATH)
    # overwrite config_path is needed due to Singleton nature, may need a better solution
    conf.config_path = TEST_CONFIG_PATH
    conf.read_config()
    log_channel = conf.get_guild_log_channel(discord.Object(4321))
    assert log_channel == discord.Object(54321)
