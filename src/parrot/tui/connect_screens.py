"""Textual screens for data source connection flow."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container, Center, Middle
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
    ConnectionDetails,
)


class DataSourceSelectScreen(Screen):
    """Screen to select data source type."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
    ]

    CSS = """
    $parrot-primary: #689D6A;
    $parrot-primary-dark: #507A52;
    $parrot-primary-darker: #38573A;
    $parrot-primary-light: #80B582;
    $parrot-primary-lighter: #98CDA9;

    Screen {
        align: center middle;
    }

    #select-container {
        width: 60;
        height: auto;
        border: solid $parrot-primary-dark;
        background: $surface-darken-1;
        padding: 1 2;
    }

    #select-title {
        text-align: center;
        text-style: bold;
        color: $parrot-primary;
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
        background: $parrot-primary-dark;
    }

    ListView > ListItem.--selected {
        background: $parrot-primary;
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
                        id="source-list"
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
    $parrot-primary: #689D6A;
    $parrot-primary-dark: #507A52;
    $parrot-primary-darker: #38573A;
    $parrot-primary-light: #80B582;
    $parrot-primary-lighter: #98CDA9;

    Screen {
        align: center middle;
    }

    #connect-container {
        width: 70;
        height: auto;
        border: solid $parrot-primary-dark;
        background: $surface-darken-1;
        padding: 1 2;
    }

    #connect-title {
        text-align: center;
        text-style: bold;
        color: $parrot-primary;
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
    }

    .input-field {
        width: 1fr;
        border: solid $parrot-primary-dark;
    }

    .input-field:focus {
        border: solid $parrot-primary;
    }

    #button-row {
        height: auto;
        margin-top: 1;
        align: center middle;
    }

    #connect-btn {
        margin-right: 1;
        background: $parrot-primary;
    }

    #connect-btn:hover {
        background: $parrot-primary-light;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            with Middle():
                with Container(id="connect-container"):
                    yield Static("SQL Database Connection", id="connect-title")

                    with Horizontal(classes="input-row"):
                        yield Label("User:", classes="input-label")
                        yield Input(placeholder="postgres", value="postgres", id="user-input", classes="input-field")

                    with Horizontal(classes="input-row"):
                        yield Label("Password:", classes="input-label")
                        yield Input(placeholder="password", value="mysecretpassword", password=True, id="password-input", classes="input-field")

                    with Horizontal(classes="input-row"):
                        yield Label("Host:", classes="input-label")
                        yield Input(placeholder="localhost", value="172.17.0.4", id="host-input", classes="input-field")

                    with Horizontal(classes="input-row"):
                        yield Label("Port:", classes="input-label")
                        yield Input(placeholder="5432", value="5432", id="port-input", classes="input-field")

                    with Horizontal(classes="input-row"):
                        yield Label("Database:", classes="input-label")
                        yield Input(placeholder="database", value="netflix", id="database-input", classes="input-field")

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
    $parrot-primary: #689D6A;
    $parrot-primary-dark: #507A52;
    $parrot-primary-darker: #38573A;
    $parrot-primary-light: #80B582;
    $parrot-primary-lighter: #98CDA9;

    Screen {
        align: center middle;
    }

    #file-container {
        width: 70;
        height: auto;
        border: solid $parrot-primary-dark;
        background: $surface-darken-1;
        padding: 1 2;
    }

    #file-title {
        text-align: center;
        text-style: bold;
        color: $parrot-primary;
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
    }

    .input-field {
        width: 1fr;
        border: solid $parrot-primary-dark;
    }

    .input-field:focus {
        border: solid $parrot-primary;
    }

    #button-row {
        height: auto;
        margin-top: 1;
        align: center middle;
    }

    #connect-btn {
        margin-right: 1;
        background: $parrot-primary;
    }

    #connect-btn:hover {
        background: $parrot-primary-light;
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
                        yield Input(placeholder=f"/path/to/file.{self.file_type}", id="path-input", classes="input-field")

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
