import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.style import Style
from rich.text import Text

from ui.chat_reponse import StyledChatResponse


class ChatInterface:
    def __init__(self, agent, data_source_type):
        # Initialize Rich console and chat styler
        self.console = Console()
        self.chat_styler = StyledChatResponse(self.console)

        # Your existing initialization
        self.agent = agent
        self.data_source_type = data_source_type
        self.chat_history = []

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
        self.chat_history.append((sender, styled_message))

    def render_chat_history(self):
        """
        Render the entire chat history with rich styling.
        """
        self.console.clear()
        self.display_header()

        for sender, styled_message in self.chat_history:
            # Directly print the styled message
            self.console.print(styled_message)

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
            if hasattr(result, 'content'):
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
        header = Panel(
            Text("Parrot 🦜: Talk to your data!", style="bold cyan", justify="center"),
            style="blue",
            expand=True,

        )
        self.console.print(header)

    def run(self):
        """
        Main application loop with enhanced styling.
        """
        self.display_header()

        while True:
            # Render current chat history
            self.render_chat_history()

            # Prompt for user input
            try:
                user_query = Prompt.ask("[bold blue]>>>[/]", console=self.console)

                if not user_query:
                    continue

                # Exit condition
                if user_query.lower() in ['exit', 'quit', 'q']:
                    break

                # Add user message to history with styling
                self.add_message(user_query, "You")

                with Progress(
                        SpinnerColumn(style="dots2"),
                        TextColumn("[progress.description]{task.description}",
                                   style=Style(color=typer.colors.WHITE, italic=True)),
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
