import os

import discord
import pytest

import python_bot.data.db_session as db_session
from python_bot.data import models
from python_bot.logger import Logger


def init_db():
    top_folder = os.path.dirname(__file__)
    rel_file = os.path.join("..", "db", "test.sqlite")
    db_file = os.path.abspath(os.path.join(top_folder, rel_file))
    db_session.global_init(db_file)


def test_get_log_channel(example_logger, example_guild, example_channel) -> None:
    # prepare db
    init_db()
    session = db_session.create_session()
    session.add(example_guild)
    session.add(example_channel)
    # query
    log_channel = Logger._get_log_channel_move(discord.Object(example_guild.id), session=session)
    assert log_channel.id == example_channel.channel_id


@pytest.fixture
def example_logger():
    return Logger()


@pytest.fixture
def example_guild():
    return models.Guild(id=123, name="Test Server", owner="Owner Name")


@pytest.fixture
def example_channel(example_guild):
    return models.Channel(channel_id=1231, channel_type_id="log_move", guild_id=example_guild.id)
