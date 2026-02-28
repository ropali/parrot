from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pathlib
from parrot.config import USER_DIR

PARROT_HOME = pathlib.Path(str(USER_DIR))

DB_PATH = PARROT_HOME / "db.sqlite"

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, future=True, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
