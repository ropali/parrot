from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from parrot.models.chat_session import ChatSession, ChatMessage


class ChatRepository:
    """Repository for chat session CRUD operations."""

    def __init__(self, db_session: Session):
        self.db = db_session

    # Session operations
    def create_session(
        self, title: Optional[str] = None, session_id: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(id=session_id or str(uuid.uuid4()), title=title)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: uuid.UUID) -> Optional[ChatSession]:
        """Get a session by ID."""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def list_sessions(self, limit: int = 50, offset: int = 0) -> List[ChatSession]:
        """List all sessions ordered by most recent first."""
        return (
            self.db.query(ChatSession)
            .order_by(desc(ChatSession.updated_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_session_title(
        self, session_id: uuid.UUID, title: str
    ) -> Optional[ChatSession]:
        """Update a session's title."""
        session = self.get_session(session_id)
        if session:
            session.title = title
            self.db.commit()
            self.db.refresh(session)
        return session

    def delete_session(self, session_id: uuid.UUID) -> bool:
        """Delete a session and all its messages. Returns True if deleted."""
        session = self.get_session(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False

    # Message operations
    def add_message(
        self,
        session_id: uuid.UUID,
        sender: str,
        raw_content: str,
        styled_content: Optional[str] = None,
    ) -> ChatMessage:
        """Add a message to a session."""
        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            sender=sender,
            raw_content=raw_content,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_message(self, message_id: uuid.UUID) -> Optional[ChatMessage]:
        """Get a message by ID."""
        return self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    def get_session_messages(self, session_id: uuid.UUID) -> List[ChatMessage]:
        """Get all messages for a session in order."""
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.sequence)
            .all()
        )

    def update_message(
        self,
        message_id: uuid.UUID,
        raw_content: Optional[str] = None,
        styled_content: Optional[str] = None,
    ) -> Optional[ChatMessage]:
        """Update a message's content."""
        message = self.get_message(message_id)
        if message:
            if raw_content is not None:
                message.raw_content = raw_content
            if styled_content is not None:
                message.styled_content = styled_content
            self.db.commit()
            self.db.refresh(message)
        return message

    def delete_message(self, message_id: uuid.UUID) -> bool:
        """Delete a message. Returns True if deleted."""
        message = self.get_message(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False

    def delete_session_messages(self, session_id: str) -> int:
        """Delete all messages for a session. Returns count deleted."""
        result = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return result

    # Bulk operations
    def save_conversation(
        self,
        messages: List[tuple[str, str, Optional[str]]],
        title: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> ChatSession:
        """
        Save an entire conversation at once.

        Args:
            messages: List of (sender, raw_content, styled_content) tuples
            title: Optional session title
            session_id: Optional session ID (generated if not provided)

        Returns:
            The created ChatSession
        """
        session = self.create_session(title=title, session_id=session_id)

        for sender, raw_content, styled_content in messages:
            self.add_message(
                session_id=session.id,
                sender=sender,
                raw_content=raw_content,
                styled_content=styled_content,
            )

        return session

    def load_conversation(
        self, session_id: uuid.UUID
    ) -> Optional[tuple[ChatSession, List[ChatMessage]]]:
        """
        Load a complete conversation including session and messages.

        Returns:
            Tuple of (session, messages) or None if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        messages = self.get_session_messages(session_id)
        return (session, messages)
