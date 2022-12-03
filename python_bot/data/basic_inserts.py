import os

import discord
import sqlalchemy.orm as orm

import python_bot.data.db_session as db_session
from python_bot.data import initial_data

INSERT_TESTDATA = True

discord.Guild(13).owner.display_name

def main():
    init_db()
    insert_rows(initial_data.channel_types)
    if INSERT_TESTDATA:
        insert_rows(initial_data.guilds)
        insert_rows(initial_data.channels)


def insert_rows(rows: list):
    session: orm.Session = db_session.factory()
    for row in rows:
        session.add(row)
    session.commit()


def init_db():
    top_folder = os.path.dirname(__file__)
    rel_file = os.path.join("..", "db", "test.sqlite")
    db_file = os.path.abspath(os.path.join(top_folder, rel_file))
    db_session.global_init(db_file)


if __name__ == '__main__':
    main()
