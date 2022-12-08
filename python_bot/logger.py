import datetime
import os

import discord
from sqlalchemy.exc import NoResultFound

import python_bot.data.db_session as db_session
import python_bot.data.models as models

LOG_MOVE = "log_move"
LOG_ADMIN = "log_admin"


def init_db():
    top_folder = os.path.dirname(__file__)
    rel_file = os.path.join("db", "config.sqlite")
    db_file = os.path.abspath(os.path.join(top_folder, rel_file))
    db_session.global_init(db_file)


class Logger:
    def __init__(self):
        init_db()
        ...

    @staticmethod
    def get_log_channel(guild: discord.Object, command_type: str) -> discord.Object | None:
        """returns a `TextChannel` or `Thread` which is used to log usage of specified command type,
        hence a channel type agnostic `discord.Object` is returned"""
        session = db_session.create_session()
        try:
            channel: models.Channel = session.query(models.Channel) \
                .filter(models.Channel.guild_id == guild.id,
                        models.Channel.channel_type_id == command_type).one()
            return discord.Object(id=channel.channel_id, type=discord.PartialMessageable)
        except NoResultFound:
            return None

    @staticmethod
    def set_log_channel(channel: discord.TextChannel | discord.Thread, command_type: str, guild: discord.Guild):
        session = db_session.create_session()
        is_thread = True if type(channel) == discord.Thread else False
        try:
            log_channel: models.Channel = session.query(models.Channel) \
                .filter(models.Channel.guild_id == guild.id,
                        models.Channel.channel_type_id == command_type).one()
        except NoResultFound:
            # INSERT new row
            session.add(models.Channel(
                channel_id=channel.id, channel_type_id=command_type, guild_id=guild.id, is_thread=is_thread))
        else:
            # UPDATE existing row
            log_channel.channel_id = channel.id
            log_channel.is_thread = is_thread
            log_channel.updated_at = datetime.datetime.now()
        finally:
            session.commit()
            return


if __name__ == '__main__':
    logger = Logger()
