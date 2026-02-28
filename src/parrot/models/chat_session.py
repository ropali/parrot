from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String,
    DateTime,
    Text,
    ForeignKey,
    func,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from parrot.db.base_model import Base


class ChatSession(Base):
    """Represents a chat session/conversation."""

    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    """Individual message within a chat session."""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False
    )
    sender: Mapped[str] = mapped_column(String, nullable=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )

    session: Mapped["ChatSession"] = relationship(back_populates="messages")

    __table_args__ = (
        UniqueConstraint(
            "session_id", "created_at", name="uq_chat_messages_session_sequence"
        ),
    )
