from parrot.rag.storage.db import engine
from parrot.db.base_model import Base
from parrot.rag.models import *  # noqa
from parrot.models.chat_session import *  # noqa


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
