"""SQLAlchemy engine/session factory."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required")
    return url


def session_factory() -> sessionmaker[Session]:
    engine = create_engine(database_url(), pool_pre_ping=True, future=True)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def session_scope() -> Iterator[Session]:
    factory = session_factory()
    with factory() as session:
        with session.begin():
            yield session
