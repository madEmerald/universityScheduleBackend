import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session, declarative_base

def global_init(server_name, password, db_name):
    global __factory

    if __factory:
        return

    if not db_name or not db_name.strip():
        raise Exception("Необходимо указать имя базы данных.")

    conn_str = f"postgresql+psycopg2://{server_name}:{password}@localhost/{db_name}"
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()


SqlAlchemyBase = declarative_base()

__factory = None
