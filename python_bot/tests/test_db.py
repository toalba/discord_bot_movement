import os

import pytest

import python_bot.data.db_session as db_session
import python_bot.data.models as models
from python_bot.data.models import ChannelType


def init_db():
    top_folder = os.path.dirname(__file__)
    rel_file = os.path.join("..", "db", "test.sqlite")
    db_file = os.path.abspath(os.path.join(top_folder, rel_file))
    db_session.global_init(db_file)


def test_channel_type() -> None:
    init_db()
    session = db_session.create_session()
    res = session.query(ChannelType)
    assert res.count() > 1
    channel_types = session.query(models.ChannelType).all()
    for ct in channel_types:
        print(ct)


def test_add_guild(example_guild) -> None:
    init_db()
    session = db_session.create_session()
    session.add(example_guild)
    print(session.query(models.Guild).first())
    session.rollback()
    session.close()


def test_add_channel(example_guild, example_channel) -> None:
    init_db()
    session = db_session.create_session()
    session.add(example_guild)
    session.add(example_channel)
    channel = session.query(models.Channel).first()
    print(channel)
    print(session.query(models.Guild).filter(models.Guild.id == channel.guild_id).one())
    session.rollback()
    session.close()


@pytest.fixture
def example_guild():
    return models.Guild(id=123, name="Test Server", owner="Owner Name")


@pytest.fixture
def example_channel(example_guild):
    return models.Channel(channel_id=1231, channel_type_id="log_move", guild_id=example_guild.id)
