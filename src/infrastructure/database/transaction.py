"""Explicit transaction boundary for application services."""

from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy.orm import Session


@contextmanager
def transaction(session: Session) -> Iterator[Session]:
    """Commit on success and roll back on failure."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
