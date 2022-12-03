from sqlalchemy import create_engine
import sqlalchemy.orm as orm

from python_bot.data.modelbase import SqlAlchemyBase

factory = None


def global_init(db_file: str):
    global factory

    if factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("You must specify a db file.")

    connection_string = "sqlite:///" + db_file.strip()
    print(f"Connecting to DB with {connection_string}")

    engine = create_engine(connection_string, echo=True)

    factory = orm.sessionmaker(bind=engine)

    # noinspection PyUnresolvedReferences
    import python_bot.data.__all_models

    SqlAlchemyBase.metadata.create_all(engine)
