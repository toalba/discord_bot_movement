import datetime

import sqlalchemy.orm as orm
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

from .modelbase import SqlAlchemyBase


class Guild(SqlAlchemyBase):
    __tablename__ = "guild"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)
    name = Column(String, nullable=True)
    owner = Column(String, nullable=True)

    channels = orm.relationship("Channel", back_populates="")

    def __repr__(self):
        return f"<Package {self.id}>"


class ChannelType(SqlAlchemyBase):
    __tablename__ = "channel_type"
    id = Column(String, primary_key=True)
    description = Column(String, nullable=True)


class Channel(SqlAlchemyBase):
    __tablename__ = "channel"
    channel_type_id = Column(ForeignKey("channel_type.id"), primary_key=True)
    channel_id = Column(Integer, nullable=False)
    guild_id = Column(ForeignKey("guild.id"), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)
