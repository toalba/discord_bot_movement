import os
from typing import List

import discord
import sqlalchemy.orm as orm
from discord import Interaction, VoiceChannel, User

import python_bot.data.db_session as db_session
import python_bot.data.models as models


def init_db():
    top_folder = os.path.dirname(__file__)
    rel_file = os.path.join("db", "test.sqlite")
    db_file = os.path.abspath(os.path.join(top_folder, rel_file))
    db_session.global_init(db_file)


class Logger:
    def __init__(self):
        init_db()
        ...

    @staticmethod
    def _get_log_channel_move(guild: discord.Object, session: orm.Session) -> discord.Object:
        channel: models.Channel = session.query(models.Channel).filter(models.Channel.channel_type_id == "log_move",
                                                                       models.Channel.guild_id == guild.id).one()
        return discord.Object(channel.channel_id)

    def log_move(self, interaction: Interaction,
                 source_channel: VoiceChannel,
                 destination_channel: VoiceChannel,
                 users: List[User]):
        pass


if __name__ == '__main__':
    logger = Logger()
