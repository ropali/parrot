import typer
from prompt_toolkit.formatted_text import FormattedText
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.style import Style
from rich.text import Text

from exporter import Exporter
from prompter import ExportPrompter
from ui.chat_reponse import StyledChatResponse
from ui.help.help_display import HelpDisplay
from ui.input_prompt import InputPrompt
from data_models import Message, Conversation


class ChatInterface:
    def __init__(self):
        # Initialize Rich console and chat styler
        self.console = Console()
        self.chat_styler = StyledChatResponse(self.console)

        self.agent = None
        self.data_source_type = None
        self.chat_history = Conversation()

    def add_message(self, message: str, sender: str):
        """
        Add a message to the chat history and render it with rich styling.

        Args:
            message: The content of the message
            sender: Who sent the message (e.g., 'You', 'Parrot')
        """
        # Create styled text for the message
        styled_message = self.chat_styler.create_message_text(message, sender)

        # Store the message in history
        self.chat_history.append(Message(sender, styled_message))

    def render_chat_history(self):
        """
        Render the entire chat history with rich styling.
        """

        for message in self.chat_history:
            # Directly print the styled message
            self.console.print(message.content)

    def process_query(self, query: str):
        """
        Process the user query and generate a styled response.

        Args:
            query: User's input query

        Returns:
            Processed response from the agent
        """
        try:
            # Process the query with your agent
            result = self.agent.run(query)

            # Extract content
            if hasattr(result, "content"):
                response = result.content
            else:
                response = str(result)

            # Add the Parrot's response with styling
            self.add_message(response, "Parrot")

            return response

        except Exception as e:
            # Handle and style error messages
            error_message = f"Error processing query: {str(e)}"
            self.add_message(error_message, "Error")
            return error_message

    def display_header(self):
        """
        Create and display the application header with rich styling.
        """

        self.console.clear()

        header = Panel(
            Text("Parrot 🦜: Talk to your data!", style="bold cyan", justify="center"),
            style="blue",
            expand=True,
        )
        self.console.print(header)

    def handle_command(self, cmd: str):
        """
        Handle special commands starting with '/'

        This method processes command-line style instructions that provide
        additional functionality like help, export, and quitting the application.
        """
        if cmd.startswith("/q"):
            return False

        if cmd.startswith("/?"):
            # Create a styled header for the help section
            help_display = HelpDisplay(self.console)
            help_display.display_help()

        if cmd.startswith("/export"):
            export_type, file_path = ExportPrompter().prompt()

            exporter = Exporter(self.chat_history)
            exporter.export(export_type, file_path)

            return None

        return True

    def run(self, agent, data_source_type):
        """
        Main application loop with enhanced styling and dynamic hint.
        """
        self.agent = agent
        self.data_source_type = data_source_type

        self.display_header()

        while True:
            # Render current chat history
            self.render_chat_history()

            try:

                user_query = InputPrompt().ask(
                    ">>> ",
                    FormattedText(
                        [
                            ("#949494 italic", "Ask your question (/? for help)"),
                        ]
                    ),
                )

                if not user_query:
                    continue

                response = self.handle_command(user_query)

                # Exit condition
                if response is False:
                    break

                if response is None:
                    continue

                # Add user message to history with styling
                self.add_message(user_query, "You")

                with Progress(
                    SpinnerColumn(style="dots2"),
                    TextColumn(
                        "[progress.description]{task.description}",
                        style=Style(color=typer.colors.WHITE, italic=True),
                    ),
                    transient=True,
                ) as progress:
                    progress.add_task(description="Processing...", total=None)
                    self.process_query(user_query)

                # Render the updated chat history
                self.render_chat_history()

            except KeyboardInterrupt:
                break

        # Farewell message
        self.console.print("[bold red]Goodbye! 👋[/]")
