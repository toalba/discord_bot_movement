import datetime

from python_bot.data.models import ChannelType, Guild, Channel

# Channel Types
channel_types = list()
channel_types.append(ChannelType(
    id="log_move",
    description="log the usage of commands for moving multiple voice users"))

# test data
guilds = list()
guilds.append(Guild(
    id=123,
    name="Test Server Private"))
guilds.append(Guild(
    id=122,
    name="Test Server Public"))
guilds.append(Guild(
    id=111,
    name="Production Server"))

channels = list()
channels.append(Channel(
    channel_type_id="log_move",
    channel_id=1231,
    guild_id=123))
