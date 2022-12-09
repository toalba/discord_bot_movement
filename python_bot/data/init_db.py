import os

import python_bot.data.db_session as db_session
import python_bot.data.models as models
from python_bot.data import initial_data


def main(filename: str):
    init_db(filename=filename)
    session = db_session.create_session()
    if session.query(models.ChannelType).count() > 0:
        print("Nothing inserted: Table 'ChannelType' is not empty")
        return
    insert_rows(initial_data.channel_types)


def insert_rows(rows: list):
    session = db_session.create_session()
    for row in rows:
        session.add(row)
    session.commit()


def init_db(filename: str) -> None:
    top_folder = os.path.dirname(__file__)
    rel_file = os.path.join("..", "db", filename)
    db_file = os.path.abspath(os.path.join(top_folder, rel_file))
    db_session.global_init(db_file)


def init_test_db():
    init_db("test.sqlite")


if __name__ == '__main__':
    main("config.sqlite")
