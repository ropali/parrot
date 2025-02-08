from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ui.help.help_content import HelpContent


class HelpDisplay:
    """Handles the presentation of help content."""

    def __init__(self, console: Console):
        self.console = console
        self.content = HelpContent()

    def create_header(self) -> Panel:
        """Creates the header panel for the help display."""
        return Panel(
            Text(self.content.header_title, style=self.content.styles['header']['text_style'], justify="center"),
            style=self.content.styles['header']['border_style'],
            expand=False
        )

    def create_commands_table(self) -> Table:
        """Creates the table displaying all available commands."""
        table = Table(
            show_header=True,
            header_style=self.content.styles['table']['header_style'],
            border_style=self.content.styles['table']['border_style'],
            expand=False
        )

        # Add columns
        table.add_column("Command", style=self.content.styles['table']['command_style'], no_wrap=True)
        table.add_column("Description", style=self.content.styles['table']['description_style'])
        table.add_column("Example", style=self.content.styles['table']['example_style'])

        # Add rows for each command
        for cmd in self.content.commands:
            table.add_row(cmd.command, cmd.description, cmd.example)

        return table

    def create_usage_notes(self) -> Panel:
        """Creates the usage notes panel."""
        return Panel(
            Text.from_markup(
                self.content.usage_notes,
                style=self.content.styles['notes']['text_style']
            ),
            title="Usage Notes",
            border_style=self.content.styles['notes']['border_style'],
            expand=False
        )

    def display_help(self):
        """Displays the complete help information."""
        self.console.print(self.create_header())
        self.console.print(self.create_commands_table())
        self.console.print(self.create_usage_notes())