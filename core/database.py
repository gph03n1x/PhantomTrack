from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import core.settings as settings


def get_engine(url):
    return create_engine(url, echo=settings.DB_ECHO)


def create_db_session(db_url):
    db_session = scoped_session(sessionmaker())
    engine = get_engine(db_url)
    db_session.configure(bind=engine)

    from core.models import Base
    Base.metadata.bind = engine

    return db_session