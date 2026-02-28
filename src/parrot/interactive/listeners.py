# Observer Pattern for Chat Events
from parrot.db.repositories.chat_repository import ChatRepository
import uuid
from typing import Protocol

from parrot.data_models import Message


class ChatEventListener(Protocol):
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    def on_message_added(self, message: Message, session_id: uuid.UUID) -> None:
        pass

    def on_chat_cleared(self) -> None:
        pass


class ChatMessageDBSaveListener:
    def __init__(self, repo: ChatRepository):
        self.repo = repo

    def on_message_added(self, message: Message, session_id: uuid.UUID) -> None:
        self.repo.add_message(
            session_id=session_id,
            sender=message.sender,
            raw_content=message.raw_content,
        )

    def on_chat_cleared(self) -> None:
        pass
