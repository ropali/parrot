from typing import Generator
from sqlalchemy.orm import Session
from parrot.rag.storage.db import SessionLocal


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session.
    
    Usage:
        db = next(get_session())
        try:
            # Use db
        finally:
            db.close()
    
    Or with context manager pattern:
        with next(get_session()) as db:
            # Use db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
