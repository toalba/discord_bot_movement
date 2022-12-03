import sqlalchemy.orm as orm
from sqlalchemy import create_engine

from python_bot.data.modelbase import SqlAlchemyBase

__factory = None


def global_init(db_file: str):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("You must specify a db file.")

    connection_string = "sqlite:///" + db_file.strip()
    print(f"Connecting to DB with {connection_string}")

    engine = create_engine(connection_string, echo=True)
    __factory = orm.sessionmaker(bind=engine)

    # noinspection PyUnresolvedReferences
    import python_bot.data.__all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> orm.Session:
    global __factory
    return __factory()
