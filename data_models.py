from dataclasses import dataclass, field
from enum import StrEnum
from typing import Iterator, List
from rich.text import Text

@dataclass
class Message:
    sender: str
    content: Text
    plain_content: str = field(init=False)

    def __post_init__(self):
        self.plain_content = self.content._text

    def __str__(self):
        return f"{self.sender}: {self.content}"

    def to_dict(self):
        return {"sender": self.sender, "content": self.plain_content}


@dataclass
class Conversation(list):
    _messages: List[Message] = field(default_factory=list)

    def append(self, message: Message):
        super().append(message)
        self._messages.append(message)

    def __iter__(self) -> Iterator[Message]:
        return iter(self._messages)

    def __str__(self):
        return f"<Conversation: {len(self._messages)} messages>"

    def __getitem__(self, index):
        return self._messages[index]

    def __len__(self):
        return len(self._messages)

    def get_messages(self) -> List[Message]:
        """Provide a clean interface for exporters to access messages"""
        return self._messages
