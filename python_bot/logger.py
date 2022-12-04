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
    def get_log_channel_move(guild: discord.Object) -> discord.Object:
        session = db_session.create_session()
        channel: models.Channel = session.query(models.Channel) \
            .filter(models.Channel.guild_id == guild.id,
                    models.Channel.channel_type_id == LOG_MOVE).one()
        return discord.Object(channel.channel_id)

    @staticmethod
    def get_log_channel_admin(guild: discord.Guild) -> discord.Object | None:
        session = db_session.create_session()
        try:
            channel: models.Channel = session.query(models.Channel) \
                .filter(models.Channel.guild_id == guild.id,
                        models.Channel.channel_type_id == LOG_ADMIN).one()
        except NoResultFound:
            return None
        else:
            return discord.Object(channel.channel_id)

    @staticmethod
    def set_log_channel(channel: discord.TextChannel | discord.Thread, log_type: str, guild: discord.Guild):
        session = db_session.create_session()
        try:
            log_channel: models.Channel = session.query(models.Channel) \
                .filter(models.Channel.guild_id == guild.id,
                        models.Channel.channel_type_id == log_type).one()
        except NoResultFound:
            # INSERT new row
            session.add(models.Channel(
                channel_id=channel.id, channel_type_id=log_type, guild_id=guild.id))
        else:
            log_channel.channel_id = channel.id
            log_channel.updated_at = datetime.datetime.now()
            session.commit()
        finally:
            return

    @staticmethod
    def set_log_channel_move(channel: discord.Object, guild: discord.Object, is_thread=False) -> None:
        session = db_session.create_session()
        try:
            log_channel: models.Channel = session.query(models.Channel) \
                .filter(models.Channel.guild_id == guild.id,
                        models.Channel.channel_type_id == LOG_MOVE).one()
        except NoResultFound:
            session.add(models.Channel(
                channel_id=channel.id, channel_type_id=LOG_MOVE, guild_id=guild.id, is_thread=is_thread))
            session.commit()
        else:
            log_channel.channel_id = channel.id
            log_channel.updated_at = datetime.datetime.now()
            session.commit()
        finally:
            return


if __name__ == '__main__':
    logger = Logger()
