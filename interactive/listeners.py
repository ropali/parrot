# Observer Pattern for Chat Events
from typing import Protocol

from data_models import Message


class ChatEventListener(Protocol):
    def on_message_added(self, message: Message) -> None:
        pass

    def on_chat_cleared(self) -> None:
        pass