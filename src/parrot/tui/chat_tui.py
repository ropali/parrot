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
from parrot.tui.connect_screens import (
    DataSourceSelectScreen,
    SQLConnectionScreen,
    FileConnectionScreen,
)


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


class AutocompleteListItem(ListItem):
    """List item for command autocomplete."""

    def __init__(self, command: str, description: str, **kwargs):
        self.command = command
        self.description = description
        super().__init__(Label(f"{command}  {description}"), **kwargs)


class ChatTUI(App):
    """Modern, compact Textual TUI for Parrot Chat with cyan theme."""

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False, priority=True),
        Binding("ctrl+q", "quit", "Quit", show=False),
        Binding("escape", "dismiss_autocomplete", "Dismiss", show=False),
        Binding("down", "focus_autocomplete", "Focus Autocomplete", show=False),
        Binding("tab", "focus_autocomplete", "Focus Autocomplete", show=False),
    ]

    # Command suggestions
    COMMANDS = [
        ("/connect", "Connect to a data source"),
        ("/help", "Show available commands"),
        ("/quit", "Quit the application"),
        ("/q", "Quit the application"),
        ("/?", "Show available commands"),
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
        display: block;
    }

    #banner-view.hidden {
        display: none;
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
        position: relative;
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

    #autocomplete-dropdown {
        height: auto;
        max-height: 12;
        background: $surface-darken-1;
        border: solid $parrot-primary;
        visibility: hidden;
        margin-bottom: 1;
    }

    #autocomplete-dropdown.visible {
        visibility: visible;
    }

    #autocomplete-dropdown {
        background: $surface-darken-1;
        border: none;
    }

    #autocomplete-dropdown:focus {
        border: none;
    }

    #autocomplete-dropdown > ListItem {
        padding: 0 1;
    }

    #autocomplete-dropdown > ListItem.--highlight {
        background: $parrot-primary-dark;
    }

    #autocomplete-dropdown > ListItem.--selected {
        background: $parrot-primary;
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

    .loading-message {
        color: $parrot-primary-light;
        text-style: italic;
        padding: 1 0;
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

    def __init__(self, agent=None, config=None, parrot=None, **kwargs):
        self.agent = agent
        self.config = config
        self.parrot = parrot
        self.db = SessionLocal()
        self.chat_repo = ChatRepository(self.db)
        self.sessions: list[ChatSession] = []
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        # Sidebar
        with Vertical(id="sidebar"):
            yield Static("💬 Sessions", id="sidebar-header")
            yield ListView(id="session-list")
            yield Button("➕ New Chat", id="new-session-btn", variant="primary")

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
            # Autocomplete dropdown (shown above input when typing /)
            yield ListView(id="autocomplete-dropdown")
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
        self._show_banner_view()

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
            "    Type /connect to connect to a data source",
            "    Type /help for available commands",
        ]

        # Mount each line separately for better control
        banner_container = self.query_one("#banner-lines", Vertical)
        banner_container.remove_children()
        for line in banner_lines:
            banner_container.mount(Static(line, classes="banner-line"))

    def _show_banner_view(self) -> None:
        """Show banner view and hide chat messages."""
        banner_view = self.query_one("#banner-view", Vertical)
        chat_messages = self.query_one("#chat-messages", VerticalScroll)
        banner_view.remove_class("hidden")
        chat_messages.remove_class("visible")
        banner_view.styles.display = "block"
        chat_messages.styles.display = "none"

    def _show_chat_view(self) -> None:
        """Show chat messages and hide banner view."""
        banner_view = self.query_one("#banner-view", Vertical)
        chat_messages = self.query_one("#chat-messages", VerticalScroll)
        banner_view.add_class("hidden")
        chat_messages.add_class("visible")
        banner_view.styles.display = "none"
        chat_messages.styles.display = "block"

    def watch_is_processing(self, is_processing: bool) -> None:
        """Watch for processing state changes and update UI."""
        loading = self.query_one("#loading-row", Horizontal)
        input_widget = self.query_one("#message-input", Input)
        send_btn = self.query_one("#send-btn", Button)

        # Hide the legacy loading row; we show the indicator inside chat instead.
        loading.styles.display = "none"

        if is_processing:
            input_widget.disabled = True
            send_btn.disabled = True
        else:
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
            self._show_chat_view()
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
        messages_container.refresh(layout=True)

    def _show_loading_message(self) -> None:
        """Show a loading indicator inside the chat messages."""
        messages_container = self.query_one("#chat-messages", VerticalScroll)
        for child in list(messages_container.children):
            if isinstance(child, Static) and "loading-message" in child.classes:
                return
        messages_container.mount(Static("🦜 Parrot is thinking...", classes="loading-message"))
        messages_container.scroll_end()
        messages_container.refresh(layout=True)

    def _hide_loading_message(self) -> None:
        """Remove the loading indicator from the chat messages."""
        messages_container = self.query_one("#chat-messages", VerticalScroll)
        for child in list(messages_container.children):
            if isinstance(child, Static) and "loading-message" in child.classes:
                child.remove()
        messages_container.refresh(layout=True)

    def send_message(self, content: str) -> None:
        """Send a message and get response."""
        if not content.strip():
            return

        # Clear input
        input_widget = self.query_one("#message-input", Input)
        input_widget.value = ""

        # Check for commands first
        if self.handle_command(content):
            return

        # Auto-create session if none exists
        if not self.current_session_id:
            self.create_new_session()
        self._show_chat_view()

        # Add user message
        timestamp = datetime.now()
        self.chat_repo.add_message(
            session_id=self.current_session_id,
            sender="You",
            raw_content=content
        )
        self.add_message_widget("You", content, timestamp)

        # Process agent response asynchronously
        if self.agent:
            self.is_processing = True
            self._show_loading_message()
            self.run_worker(self._process_agent_response_worker(content), exclusive=True)
        else:
            # Show message that user needs to connect
            self.is_processing = True
            response_time = datetime.now()
            response_content = "Not connected to any data source. Type /connect to connect."
            self.chat_repo.add_message(
                session_id=self.current_session_id,
                sender="System",
                raw_content=response_content
            )
            self.add_message_widget("System", response_content, response_time)
            self.set_timer(0.2, self._stop_processing)

    def _stop_processing(self) -> None:
        """Stop the loading indicator."""
        self.is_processing = False

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
            self._hide_loading_message()
            self.is_processing = False

    def run_threaded(self, func, *args, **kwargs):
        """Helper to run a blocking function in a thread."""
        import asyncio
        return asyncio.to_thread(func, *args, **kwargs)

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle session selection."""
        if event.list_view.id == "autocomplete-dropdown":
            if isinstance(event.item, AutocompleteListItem):
                self._apply_autocomplete_command(event.item.command)
            return

        if isinstance(event.item, SessionListItem):
            self.select_session(event.item.session.id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new-session-btn":
            self.create_new_session()
        elif event.button.id == "send-btn":
            input_widget = self.query_one("#message-input", Input)
            dropdown = self.query_one("#autocomplete-dropdown", ListView)
            if dropdown.has_class("visible"):
                command = self._get_autocomplete_selection()
                if command:
                    self._apply_autocomplete_command(command)
                    return
            self.send_message(input_widget.value)

    def handle_command(self, content: str) -> bool:
        """Handle /commands. Returns True if command was handled."""
        content = content.strip()

        # Hide autocomplete dropdown
        dropdown = self.query_one("#autocomplete-dropdown", ListView)
        dropdown.remove_class("visible")

        if content == "/connect":
            self.push_screen(DataSourceSelectScreen(), self._on_source_selected)
            return True

        elif content == "/quit" or content == "/q":
            self.exit()
            return True

        elif content == "/help" or content == "/?":
            help_text = """Available commands:
/connect - Connect to a data source
/help or /? - Show this help message
/quit or /q - Quit the application"""
            self.notify(help_text, severity="information", timeout=10)
            return True

        return False

    def _on_source_selected(self, source_type: Optional[str]) -> None:
        """Handle data source selection."""
        if source_type is None:
            return

        if source_type == "sql":
            self.push_screen(SQLConnectionScreen(), self._on_connection_details)
        elif source_type == "csv":
            self.push_screen(FileConnectionScreen(file_type="csv"), self._on_connection_details)
        elif source_type == "parquet":
            self.push_screen(FileConnectionScreen(file_type="parquet"), self._on_connection_details)

    def _on_connection_details(self, details) -> None:
        """Handle connection details and initialize agent."""
        if details is None:
            return

        if self.parrot:
            # Set the data source type based on details
            if hasattr(details, 'to_connection_string'):
                self.parrot.data_source_type = "sql"
            elif hasattr(details, 'extension'):
                self.parrot.data_source_type = details.extension.lstrip('.')

            # Create the agent directly
            from parrot.llm_loader import LLMModelLoader
            from parrot.agents.factory import AgentsFactory

            model = LLMModelLoader.load(
                self.parrot.config.provider,
                self.parrot.config.model,
                self.parrot.config.api_key
            )
            self.parrot.agent = AgentsFactory().create(model, details)
            self.agent = self.parrot.agent

            self.notify(f"Connected to {self.parrot.data_source_type}!", severity="success")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for autocomplete."""
        if event.input.id == "message-input":
            self._handle_autocomplete(event.value)

    def _handle_autocomplete(self, text: str) -> None:
        """Show/hide autocomplete based on input."""
        try:
            dropdown = self.query_one("#autocomplete-dropdown", ListView)
        except Exception:
            # Dropdown not found, skip
            return
        
        if text.startswith("/"):
            # Filter commands that match
            matching_commands = [
                (cmd, desc) for cmd, desc in self.COMMANDS
                if cmd.startswith(text)
            ]
            
            if matching_commands:
                dropdown.clear()
                for cmd, desc in matching_commands:
                    dropdown.append(AutocompleteListItem(cmd, desc))
                dropdown.add_class("visible")
                return
        
        # Hide dropdown if not matching
        dropdown.remove_class("visible")

    def action_dismiss_autocomplete(self) -> None:
        """Dismiss the autocomplete dropdown."""
        dropdown = self.query_one("#autocomplete-dropdown", ListView)
        dropdown.remove_class("visible")
        self.set_focus(self.query_one("#message-input", Input))

    def action_focus_autocomplete(self) -> None:
        """Move focus to the autocomplete list if visible."""
        dropdown = self.query_one("#autocomplete-dropdown", ListView)
        if not dropdown.has_class("visible"):
            return
        if dropdown.index is None and len(dropdown.children) > 0:
            dropdown.index = 0
        self.set_focus(dropdown)

    def _get_autocomplete_selection(self) -> Optional[str]:
        """Return the currently highlighted autocomplete command, if any."""
        dropdown = self.query_one("#autocomplete-dropdown", ListView)
        if not dropdown.has_class("visible"):
            return None
        if dropdown.index is None:
            return None
        items = list(dropdown.children)
        if dropdown.index < 0 or dropdown.index >= len(items):
            return None
        item = items[dropdown.index]
        if not isinstance(item, AutocompleteListItem):
            return None
        return item.command

    def _apply_autocomplete_command(self, command: str) -> None:
        """Apply and send an autocomplete command."""
        dropdown = self.query_one("#autocomplete-dropdown", ListView)
        input_widget = self.query_one("#message-input", Input)
        input_widget.value = command
        input_widget.cursor_position = len(command)
        dropdown.remove_class("visible")
        self.set_focus(input_widget)
        self.send_message(command)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "message-input":
            # Hide autocomplete dropdown
            dropdown = self.query_one("#autocomplete-dropdown", ListView)
            if dropdown.has_class("visible"):
                command = self._get_autocomplete_selection()
                if command:
                    self._apply_autocomplete_command(command)
                    return
            dropdown.remove_class("visible")

            self.send_message(event.value)


def run_tui(agent=None, config=None, parrot=None):
    """Run the chat TUI."""
    app = ChatTUI(agent=agent, config=config, parrot=parrot)
    return app.run()


if __name__ == "__main__":
    run_tui()
