import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from src.infrastructure.database.transaction import transaction


def test_transaction_commits_on_success() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("create table events (id integer primary key, value text not null)"))
    with Session(engine) as session:
        with transaction(session):
            session.execute(text("insert into events (id, value) values (1, 'ok')"))
    with Session(engine) as session:
        assert session.scalar(text("select value from events where id = 1")) == "ok"


def test_transaction_rolls_back_on_failure() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("create table events (id integer primary key, value text not null)"))
    with Session(engine) as session:
        with pytest.raises(RuntimeError):
            with transaction(session):
                session.execute(text("insert into events (id, value) values (1, 'bad')"))
                raise RuntimeError("boom")
    with Session(engine) as session:
        assert session.scalar(text("select count(*) from events")) == 0
