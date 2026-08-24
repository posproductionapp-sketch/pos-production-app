"""Application transaction boundary."""

from contextlib import AbstractContextManager
from sqlalchemy.orm import Session


class UnitOfWork(AbstractContextManager):
    """Own commit/rollback; repositories must never commit implicitly."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def __enter__(self) -> "UnitOfWork":
        self.session.begin()
        return self

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        if self.session.in_transaction():
            self.session.rollback()

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None:
            self.rollback()
        elif self.session.in_transaction():
            self.commit()
        return False
