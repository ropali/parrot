from dataclasses import dataclass


@dataclass
class CommandInfo:
    """Represents a single command and its documentation."""
    command: str
    description: str
    example: str


class HelpContent:
    """Manages the content and structure of the help system."""

    def __init__(self):
        # Define all available commands
        self.commands = [
            CommandInfo(
                command="/q",
                description="Quit the application",
                example="/q"
            ),
            CommandInfo(
                command="/export",
                description="Export the current chat history to a file",
                example="/export"
            ),
            CommandInfo(
                command="/?",
                description="Display this help message",
                example="/?"
            )
        ]

        # Define section titles and messages
        self.header_title = "Available Commands"
        self.usage_notes = (
            "Type any message to chat with your data\n"
            "Commands start with '/' and provide additional functionality"
        )

        # Define styling configuration
        self.styles = {
            'header': {
                'text_style': "bold cyan",
                'border_style': "blue",
            },
            'table': {
                'header_style': "bold cyan",
                'border_style': "blue",
                'command_style': "cyan",
                'description_style': "white",
                'example_style': "dim",
            },
            'notes': {
                'text_style': "dim",
                'border_style': "blue",
            }
        }