import pytest

import python_bot.data.db_session as db_session
import python_bot.data.init_db as init_db
import python_bot.data.models as models
from python_bot.data.models import ChannelType


def test_channel_type() -> None:
    init_db.main("test.sqlite")
    session = db_session.create_session()
    res = session.query(ChannelType)
    assert res.count() > 0
    channel_types = session.query(models.ChannelType).all()
    for ct in channel_types:
        print(f"{ct} {ct.description}")


def test_add_guild(example_guild) -> None:
    init_db.main("test.sqlite")
    session = db_session.create_session()
    session.add(example_guild)
    guild = session.query(models.Guild).first()
    print(f"{guild}{f' by {guild.owner}' if guild.owner else ''}")
    session.rollback()
    session.close()


def test_add_channel(example_guild, example_channel) -> None:
    init_db.main("test.sqlite")
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
