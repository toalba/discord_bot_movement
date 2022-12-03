import datetime

import sqlalchemy.orm as orm
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean

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
        res = f"<Guild {self.id}{f': {self.name}' if self.name else ''}>"
        if self.name:
            res += f": {self.name}"
        return res


class ChannelType(SqlAlchemyBase):
    __tablename__ = "channel_type"
    id = Column(String, primary_key=True)
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"<ChannelType {self.id}>"


class Channel(SqlAlchemyBase):
    __tablename__ = "channel"
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now)
    channel_id = Column(Integer, nullable=False)
    channel_type_id = Column(ForeignKey("channel_type.id"), primary_key=True)
    guild_id = Column(ForeignKey("guild.id"), primary_key=True, index=True)
    is_thread = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Channel {self.channel_type_id}: {self.channel_id}>"
