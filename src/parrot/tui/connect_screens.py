from textual.app import ComposeResult
from textual.containers import Horizontal, Container, Center, Middle
from textual.screen import Screen
from textual.widgets import (
    Button,
    Input,
    Label,
    ListView,
    ListItem,
    Static,
)
from textual.binding import Binding

from parrot.prompter import (
    SQLConnectionDetails,
    CSVConnectionDetails,
    ParquetConnectionDetails,
)


class DataSourceSelectScreen(Screen):
    """Screen to select data source type."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    CSS = """
    $parrot-bg: #0f1214;
    $parrot-panel: #151a1f;
    $parrot-panel-2: #1b2228;
    $parrot-border: #2b343c;
    $parrot-muted: #9aa6b2;
    $parrot-accent: #76c7a0;
    $parrot-accent-strong: #58b889;
    $parrot-accent-soft: #9fdcc0;
    $parrot-on-accent: #0b0f0c;

    Screen {
        align: center middle;
        background: $parrot-bg;
    }

    Button {
        border: round $parrot-border;
        background: $parrot-panel-2;
        color: $text;
        padding: 0 1;
        height: 3;
        min-width: 10;
        content-align: center middle;
    }

    Button:hover {
        border: round $parrot-accent;
        background: $parrot-panel;
    }

    Button:focus {
        border: round $parrot-accent;
    }

    Button.-error {
        background: $error;
        color: $parrot-on-accent;
        border: round $error;
    }

    Button.-error:hover {
        border: round $error;
        background: $error-darken-1;
    }

    Input {
        border: round $parrot-border;
        background: $parrot-panel-2;
        color: $text;
        padding: 0 1;
    }

    Input:focus {
        border: round $parrot-accent;
    }

    #select-container {
        width: 60;
        height: auto;
        border: round $parrot-border;
        background: $parrot-panel;
        padding: 1 2;
    }

    #select-title {
        text-align: center;
        text-style: bold;
        color: $parrot-accent;
        margin-bottom: 1;
    }

    #source-list {
        height: auto;
        border: none;
        margin: 1 0;
    }

    ListView > ListItem {
        padding: 1;
        text-align: center;
    }

    ListView > ListItem.--highlight {
        background: $parrot-panel-2;
    }

    ListView > ListItem.--selected {
        background: $parrot-accent-strong;
        color: $parrot-on-accent;
    }

    #cancel-btn {
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Container(id="select-container"):
                    yield Static("Select Data Source", id="select-title")
                    yield ListView(
                        ListItem(Label("📊 SQL Database")),
                        ListItem(Label("📄 CSV File")),
                        ListItem(Label("🗂️  Parquet File")),
                        id="source-list",
                    )
                    yield Button("Cancel", id="cancel-btn", variant="error")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle source selection."""
        sources = ["sql", "csv", "parquet"]
        if event.list_view.index < len(sources):
            self.dismiss(sources[event.list_view.index])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle cancel button."""
        if event.button.id == "cancel-btn":
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel selection."""
        self.dismiss(None)


class SQLConnectionScreen(Screen):
    """Screen to enter SQL database connection details."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    CSS = """
    $parrot-bg: #0f1214;
    $parrot-panel: #151a1f;
    $parrot-panel-2: #1b2228;
    $parrot-border: #2b343c;
    $parrot-muted: #9aa6b2;
    $parrot-accent: #76c7a0;
    $parrot-accent-strong: #58b889;
    $parrot-accent-soft: #9fdcc0;

    Screen {
        align: center middle;
        background: $parrot-bg;
    }

    #connect-container {
        width: 70;
        height: auto;
        border: round $parrot-border;
        background: $parrot-panel;
        padding: 1 2;
    }

    #connect-title {
        text-align: center;
        text-style: bold;
        color: $parrot-accent;
        margin-bottom: 1;
    }

    .input-row {
        height: auto;
        margin: 1 0;
    }

    .input-label {
        width: 15;
        content-align: right middle;
        padding-right: 1;
        color: $parrot-muted;
    }

    .input-field {
        width: 1fr;
        border: round $parrot-border;
        background: $parrot-panel-2;
        padding: 0 1;
    }

    .input-field:focus {
        border: round $parrot-accent;
    }

    #button-row {
        height: auto;
        margin-top: 1;
        align: center middle;
    }

    #connect-btn {
        margin-right: 1;
        background: $parrot-accent-strong;
        color: $parrot-on-accent;
    }

    #connect-btn:hover {
        background: $parrot-accent;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Container(id="connect-container"):
                    yield Static("SQL Database Connection", id="connect-title")

                    with Horizontal(classes="input-row"):
                        yield Label("User:", classes="input-label")
                        yield Input(
                            placeholder="postgres",
                            value="postgres",
                            id="user-input",
                            classes="input-field",
                        )

                    with Horizontal(classes="input-row"):
                        yield Label("Password:", classes="input-label")
                        yield Input(
                            placeholder="password",
                            value="mysecretpassword",
                            password=True,
                            id="password-input",
                            classes="input-field",
                        )

                    with Horizontal(classes="input-row"):
                        yield Label("Host:", classes="input-label")
                        yield Input(
                            placeholder="localhost",
                            value="172.17.0.4",
                            id="host-input",
                            classes="input-field",
                        )

                    with Horizontal(classes="input-row"):
                        yield Label("Port:", classes="input-label")
                        yield Input(
                            placeholder="5432",
                            value="5432",
                            id="port-input",
                            classes="input-field",
                        )

                    with Horizontal(classes="input-row"):
                        yield Label("Database:", classes="input-label")
                        yield Input(
                            placeholder="database",
                            value="netflix",
                            id="database-input",
                            classes="input-field",
                        )

                    with Horizontal(id="button-row"):
                        yield Button("Connect", id="connect-btn", variant="primary")
                        yield Button("Cancel", id="cancel-btn", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "connect-btn":
            details = SQLConnectionDetails(
                user=self.query_one("#user-input", Input).value,
                password=self.query_one("#password-input", Input).value,
                host=self.query_one("#host-input", Input).value,
                port=self.query_one("#port-input", Input).value,
                database=self.query_one("#database-input", Input).value,
            )
            self.dismiss(details)
        elif event.button.id == "cancel-btn":
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel connection."""
        self.dismiss(None)


class FileConnectionScreen(Screen):
    """Screen to enter file path for CSV or Parquet."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    CSS = """
    $parrot-bg: #0f1214;
    $parrot-panel: #151a1f;
    $parrot-panel-2: #1b2228;
    $parrot-border: #2b343c;
    $parrot-muted: #9aa6b2;
    $parrot-accent: #76c7a0;
    $parrot-accent-strong: #58b889;
    $parrot-accent-soft: #9fdcc0;
    $parrot-on-accent: #0b0f0c;

    Screen {
        align: center middle;
        background: $parrot-bg;
    }

    #file-container {
        width: 70;
        height: auto;
        border: round $parrot-border;
        background: $parrot-panel;
        padding: 1 2;
    }

    #file-title {
        text-align: center;
        text-style: bold;
        color: $parrot-accent;
        margin-bottom: 1;
    }

    .input-row {
        height: auto;
        margin: 1 0;
    }

    .input-label {
        width: 12;
        content-align: right middle;
        padding-right: 1;
        color: $parrot-muted;
    }

    .input-field {
        width: 1fr;
        border: round $parrot-border;
        background: $parrot-panel-2;
        padding: 0 1;
    }

    .input-field:focus {
        border: round $parrot-accent;
    }

    #button-row {
        height: auto;
        margin-top: 1;
        align: center middle;
    }

    #connect-btn {
        margin-right: 1;
        background: $parrot-accent-strong;
        color: $parrot-on-accent;
    }

    #connect-btn:hover {
        background: $parrot-accent;
    }
    """

    def __init__(self, file_type: str = "csv", **kwargs):
        self.file_type = file_type
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        title = f"{self.file_type.upper()} File Connection"
        with Center():
            with Middle():
                with Container(id="file-container"):
                    yield Static(title, id="file-title")

                    with Horizontal(classes="input-row"):
                        yield Label("File Path:", classes="input-label")
                        yield Input(
                            placeholder=f"/path/to/file.{self.file_type}",
                            id="path-input",
                            classes="input-field",
                        )

                    with Horizontal(id="button-row"):
                        yield Button("Connect", id="connect-btn", variant="primary")
                        yield Button("Cancel", id="cancel-btn", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "connect-btn":
            path = self.query_one("#path-input", Input).value
            if self.file_type == "csv":
                details = CSVConnectionDetails(file_path=path)
            else:
                details = ParquetConnectionDetails(file_path=path)
            self.dismiss(details)
        elif event.button.id == "cancel-btn":
            self.dismiss(None)

    def action_cancel(self) -> None:
        """Cancel connection."""
        self.dismiss(None)
