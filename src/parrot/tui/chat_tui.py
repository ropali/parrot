"""Textual TUI for Parrot Chat with session sidebar and chat interface."""

from datetime import datetime
from typing import Optional
import uuid
import sys

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll, Container, Center, Middle
from textual.reactive import reactive
from textual.worker import Worker, WorkerState
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    Static,
    Rule,
)
from textual.binding import Binding

from parrot.db.repositories.chat_repository import ChatRepository
from parrot.models.chat_session import ChatSession, ChatMessage
from parrot.rag.storage.db import SessionLocal
from parrot.interactive.message_processors import AgentMessageProcessor


class ChatMessageWidget(Static):
    """Compact widget to display a single chat message."""

    def __init__(self, sender: str, content: str, timestamp: datetime, **kwargs):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Horizontal(classes="message-row"):
            # Avatar/icon column
            avatar = "👤" if self.sender == "You" else "🦜" if self.sender == "Parrot" else "⚠️"
            yield Label(avatar, classes="message-avatar")

            # Content column
            with Vertical(classes="message-body"):
                with Horizontal(classes="message-meta"):
                    yield Label(self.sender, classes=f"message-sender {self.sender.lower()}")
                    yield Label(self.timestamp.strftime("%H:%M"), classes="message-time")
                yield Markdown(self.content, classes="message-text")


class SessionListItem(ListItem):
    """Compact list item for chat sessions."""

    def __init__(self, session: ChatSession, **kwargs):
        self.session = session
        title = session.title or f"Chat {session.id[:6]}"
        super().__init__(Label(f"💬 {title}"), **kwargs)


class ChatTUI(App):
    """Modern, compact Textual TUI for Parrot Chat with cyan theme."""

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("q", "quit", "Quit", show=True),
    ]

    CSS = """
    /* Custom color definitions */
    $parrot-primary: #689D6A;        /* 0.40784314, 0.6156863, 0.41568628 */
    $parrot-primary-dark: #507A52;
    $parrot-primary-darker: #38573A;
    $parrot-primary-light: #80B582;
    $parrot-primary-lighter: #98CDA9;

    /* Main layout */
    Screen {
        layout: horizontal;
        background: $surface-darken-2;
    }

    /* Sidebar - compact and clean */
    #sidebar {
        width: 20%;
        height: 100%;
        background: $surface-darken-1;
        border-right: solid $parrot-primary-dark;
    }

    #sidebar-header {
        height: auto;
        padding: 1;
        background: $parrot-primary-dark;
        color: $text;
        text-align: center;
        text-style: bold;
    }

    #session-list {
        height: 1fr;
        border: none;
        background: transparent;
        padding: 0;
    }

    #session-list:focus {
        border: none;
    }

    #new-session-btn {
        margin: 1;
        height: auto;
        background: $parrot-primary;
    }

    #new-session-btn:hover {
        background: $parrot-primary-light;
    }

    /* Chat area */
    #chat-area {
        width: 80%;
        height: 100%;
    }

    #chat-header {
        height: auto;
        padding: 1;
        background: $parrot-primary-darker;
        color: $text;
        text-style: bold;
        text-align: center;
    }

    #messages-container {
        height: 1fr;
        background: $surface-darken-2;
        padding: 0 1;
    }

    #banner-view {
        height: 100%;
        width: 100%;
    }

    #banner-spacer-top {
        height: 1fr;
    }

    #banner-lines {
        height: auto;
        width: 100%;
    }

    #banner-spacer-bottom {
        height: 1fr;
    }

    #chat-messages {
        height: 100%;
        width: 100%;
        display: none;
    }

    #chat-messages.visible {
        display: block;
    }

    #loading-row {
        height: auto;
        padding: 0 1;
        background: $surface-darken-2;
        visibility: hidden;
    }

    #loading-row.visible {
        visibility: visible;
    }

    #loading-text {
        color: $parrot-primary-light;
        text-style: italic;
    }

    #input-area {
        height: auto;
        padding: 1;
        background: $surface-darken-1;
        border-top: solid $parrot-primary-dark;
    }

    #message-input {
        width: 1fr;
        border: solid $parrot-primary-dark;
    }

    #message-input:focus {
        border: solid $parrot-primary;
    }

    #send-btn {
        margin-left: 1;
        background: $parrot-primary;
    }

    #send-btn:hover {
        background: $parrot-primary-light;
    }

    /* Message styling - compact */
    ChatMessageWidget {
        height: auto;
        margin: 0;
        padding: 0;
    }

    .message-row {
        height: auto;
        padding: 0;
        margin: 0 0 1 0;
    }

    .message-avatar {
        width: 3;
        height: auto;
        content-align: center middle;
    }

    .message-body {
        width: 1fr;
        height: auto;
    }

    .message-meta {
        height: auto;
        margin: 0 0 0 0;
    }

    .message-sender {
        text-style: bold;
        width: auto;
    }

    .message-sender.you {
        color: $parrot-primary-lighter;
    }

    .message-sender.parrot {
        color: $success;
    }

    .message-sender.error {
        color: $error;
    }

    .message-time {
        color: $text-muted;
        margin-left: 1;
        text-style: dim;
    }

    .message-text {
        color: $text;
        margin: 0;
        padding: 0;
    }

    .message-text > * {
        margin: 0;
        padding: 0;
    }

    /* Session list items */
    ListView > ListItem {
        padding: 0 1;
        height: auto;
        margin: 0;
        border: none;
    }

    ListView > ListItem > Label {
        padding: 0;
        margin: 0;
        height: auto;
    }

    ListView > ListItem.--highlight {
        background: $parrot-primary-darker;
    }

    ListView > ListItem.--selected {
        background: $parrot-primary-dark;
    }

    /* Placeholder */
    .placeholder {
        color: $text-muted;
        text-align: center;
        text-style: italic;
        padding: 2;
    }

    /* Banner styling */
    .banner-line {
        color: $parrot-primary;
        text-align: center;
        text-style: bold;
        height: auto;
        padding: 0;
        margin: 0;
        width: 100%;
        content-align: center middle;
    }
    """

    current_session_id: reactive[Optional[str]] = reactive(None)
    is_processing: reactive[bool] = reactive(False)

    def __init__(self, agent=None, config=None, **kwargs):
        self.agent = agent
        self.config = config
        self.db = SessionLocal()
        self.chat_repo = ChatRepository(self.db)
        self.sessions: list[ChatSession] = []
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        # Sidebar
        with Vertical(id="sidebar"):
            yield Static("💬 Sessions", id="sidebar-header")
            yield ListView(id="session-list")
            yield Button("➕ New", id="new-session-btn", variant="primary")

        # Chat area
        with Vertical(id="chat-area"):
            yield Static("No session selected", id="chat-header")
            with Container(id="messages-container"):
                # Banner view (shown initially)
                with Vertical(id="banner-view"):
                    yield Static("", id="banner-spacer-top")
                    with Vertical(id="banner-lines"):
                        pass
                    yield Static("", id="banner-spacer-bottom")
                # Chat messages view (shown when session selected)
                with VerticalScroll(id="chat-messages"):
                    yield Static("Select or create a session to start chatting", classes="placeholder")
            with Horizontal(id="loading-row"):
                yield Label("🦜 Parrot is thinking...", id="loading-text")
            with Horizontal(id="input-area"):
                yield Input(placeholder="Ask a question...", id="message-input")
                yield Button("Send", id="send-btn", variant="primary")

    def on_mount(self) -> None:
        """Load sessions when app mounts."""
        self.load_sessions()
        # Show banner on first run instead of loading last session
        self.show_banner()

    def show_banner(self) -> None:
        """Display the Parrot banner in the chat area."""
        header = self.query_one("#chat-header", Static)
        header.update("🦜 Welcome to Parrot")

        # Clear banner container

        # Build banner with original format
        model_info = ""
        provider_info = ""
        if self.config:
            model_info = self.config.model
            provider_info = self.config.provider

        # Create banner with proper alignment
        banner_lines = [
            "    ██████╗  █████╗ ██████╗ ██████╗  ██████╗ ████████╗",
            "    ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝",
            "    ██████╔╝███████║██████╔╝██████╔╝██║   ██║   ██║   ",
            "    ██╔═══╝ ██╔══██║██╔══██╗██╔══██╗██║   ██║   ██║   ",
            "    ██║     ██║  ██║██║  ██║██║  ██║╚██████╔╝   ██║   ",
            "    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   ",
            "",
            "        Your Intelligent AI Companion",
            "",
            f"    v1.0.0  •  Model: {model_info}  •  Provider: {provider_info}",
            "",
            "    Type a message below to start a new conversation,",
            "    or select a session from the sidebar.",
            "",
        ]

        # Mount each line separately for better control
        banner_container = self.query_one("#banner-lines", Vertical)
        banner_container.remove_children()
        for line in banner_lines:
            banner_container.mount(Static(line, classes="banner-line"))

    def watch_is_processing(self, is_processing: bool) -> None:
        """Watch for processing state changes and update UI."""
        loading = self.query_one("#loading-row", Horizontal)
        input_widget = self.query_one("#message-input", Input)
        send_btn = self.query_one("#send-btn", Button)

        if is_processing:
            loading.add_class("visible")
            input_widget.disabled = True
            send_btn.disabled = True
        else:
            loading.remove_class("visible")
            input_widget.disabled = False
            send_btn.disabled = False
            input_widget.focus()

    def load_sessions(self) -> None:
        """Load all chat sessions into the sidebar."""
        session_list = self.query_one("#session-list", ListView)
        session_list.clear()
        self.sessions = self.chat_repo.list_sessions()

        for session in self.sessions:
            session_list.append(SessionListItem(session))

    def create_new_session(self) -> None:
        """Create a new chat session."""
        session = self.chat_repo.create_session(title=f"Chat {len(self.sessions) + 1}")
        self.sessions.insert(0, session)

        session_list = self.query_one("#session-list", ListView)
        session_list.insert(0, [SessionListItem(session)])
        session_list.index = 0

        self.select_session(session.id)

    def select_session(self, session_id: str) -> None:
        """Select a session and display its messages."""
        self.current_session_id = session_id
        session = next((s for s in self.sessions if s.id == session_id), None)

        if session:
            header = self.query_one("#chat-header", Static)
            header.update(f"🦜 {session.title or f'Chat {session.id[:6]}'}")
            self.load_messages(session_id)

    def load_messages(self, session_id: str) -> None:
        """Load messages for the current session."""
        messages_container = self.query_one("#chat-messages", VerticalScroll)
        messages_container.remove_children()

        messages = self.chat_repo.get_session_messages(session_id)

        if not messages:
            messages_container.mount(
                Static("Start a conversation by typing a message below.", classes="placeholder")
            )
        else:
            for msg in messages:
                self.add_message_widget(msg.sender, msg.raw_content, msg.created_at)

        messages_container.scroll_end()

    def add_message_widget(self, sender: str, content: str, timestamp: datetime) -> None:
        """Add a message widget to the chat."""
        messages_container = self.query_one("#chat-messages", VerticalScroll)

        # Remove placeholder if present
        for child in list(messages_container.children):
            if isinstance(child, Static) and "placeholder" in child.classes:
                child.remove()

        messages_container.mount(ChatMessageWidget(sender, content, timestamp))
        messages_container.scroll_end()

    def send_message(self, content: str) -> None:
        """Send a message and get response."""
        if not content.strip():
            return

        # Auto-create session if none exists
        if not self.current_session_id:
            self.create_new_session()

        # Add user message
        timestamp = datetime.now()
        self.chat_repo.add_message(
            session_id=self.current_session_id,
            sender="You",
            raw_content=content
        )
        self.add_message_widget("You", content, timestamp)

        # Clear input
        input_widget = self.query_one("#message-input", Input)
        input_widget.value = ""

        # Process agent response asynchronously
        if self.agent:
            self.run_worker(self._process_agent_response_worker(content), exclusive=True)
        else:
            self.run_worker(self._echo_response_worker(content), exclusive=True)

    async def _echo_response_worker(self, content: str) -> None:
        """Worker to simulate echo response."""
        self.is_processing = True
        import asyncio
        await asyncio.sleep(0.5)

        response_content = f"Echo: {content}"
        response_time = datetime.now()

        self.chat_repo.add_message(
            session_id=self.current_session_id,
            sender="Parrot",
            raw_content=response_content
        )
        self.add_message_widget("Parrot", response_content, response_time)
        self.is_processing = False

    async def _process_agent_response_worker(self, query: str) -> None:
        """Worker to process agent response without blocking UI."""
        self.is_processing = True

        try:
            processor = AgentMessageProcessor(self.agent)
            response = await self.run_threaded(processor.process, query)

            timestamp = datetime.now()
            self.chat_repo.add_message(
                session_id=self.current_session_id,
                sender="Parrot",
                raw_content=response
            )
            self.add_message_widget("Parrot", response, timestamp)
        except Exception as e:
            timestamp = datetime.now()
            error_msg = f"Error: {str(e)}"
            self.chat_repo.add_message(
                session_id=self.current_session_id,
                sender="Error",
                raw_content=error_msg
            )
            self.add_message_widget("Error", error_msg, timestamp)
        finally:
            self.is_processing = False

    def run_threaded(self, func, *args, **kwargs):
        """Helper to run a blocking function in a thread."""
        import concurrent.futures
        import asyncio

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return loop.run_in_executor(pool, func, *args, **kwargs)

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle session selection."""
        if isinstance(event.item, SessionListItem):
            self.select_session(event.item.session.id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new-session-btn":
            self.create_new_session()
        elif event.button.id == "send-btn":
            input_widget = self.query_one("#message-input", Input)
            self.send_message(input_widget.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "message-input":
            self.send_message(event.value)


def run_tui(agent=None, config=None):
    """Run the chat TUI."""
    app = ChatTUI(agent=agent, config=config)
    app.run()


if __name__ == "__main__":
    run_tui()
