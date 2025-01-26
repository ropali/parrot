from typing import Union, List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text


class StyledChatResponse:
    def __init__(self, console: Console = None):
        """
        Initialize a styled chat response manager.

        Args:
            console: Optional Rich Console instance. Creates a new one if not provided.
        """
        self.console = console or Console()

    def create_message_text(self,
                            message: str,
                            sender: str,
                            styling: dict = None) -> Text:
        """
        Create a richly styled text message for chat interface.

        Args:
            message: The content of the message
            sender: Who sent the message (e.g., 'You', 'Parrot')
            styling: Optional dictionary to customize text styling

        Returns:
            A Rich Text object with styled message
        """
        # Default styling configurations
        default_styles = {
            'You': {
                'color': 'green',
                'emphasis': 'bold',
                'prefix': '👤 > '
            },
            'Parrot': {
                'color': 'magenta',
                'emphasis': 'italic',
                'prefix': '🦜 > '
            },
            'Error': {
                'color': 'red',
                'emphasis': 'bold',
                'prefix': '❌ > '
            }
        }

        # Merge default and custom styling
        style_config = default_styles.get(sender, default_styles['Parrot'])
        style_config.update(styling or {})

        # Create styled text
        styled_text = Text()

        # Add prefix
        styled_text.append(
            Text(style_config['prefix'], style=style_config['color'])
        )

        # Add message with emphasis
        styled_text.append(
            Text(
                message,
                style=f"{style_config['color']} {style_config['emphasis']}"
            )
        )

        return styled_text

    def create_code_block(self,
                          code: str,
                          language: str = 'python') -> Panel:
        """
        Create a syntax-highlighted code block.

        Args:
            code: The code to be displayed
            language: Programming language for syntax highlighting

        Returns:
            A Rich Panel with syntax-highlighted code
        """
        syntax = Syntax(
            code,
            language,
            theme='monokai',
            line_numbers=True
        )

        return Panel(
            syntax,
            title=f"[bold]{language.upper()} Code",
            border_style='dim'
        )

    def format_complex_response(self,
                                response: Union[str, List[Tuple[str, str]]]) -> Text:
        """
        Handle complex responses with multiple parts or types.

        Args:
            response: A string or list of (type, content) tuples

        Returns:
            A Rich Text object representing the entire response
        """
        if isinstance(response, str):
            return self.create_message_text(response, 'Parrot')

        formatted_response = Text()
        for content_type, content in response:
            if content_type == 'text':
                formatted_response.append(
                    self.create_message_text(content, 'Parrot')
                )
            elif content_type == 'code':
                formatted_response.append('\n')
                formatted_response.append(
                    self.create_code_block(content)
                )
                formatted_response.append('\n')

        return formatted_response

    def render(self, response: Union[str, List[Tuple[str, str]]]):
        """
        Render and display the formatted response.

        Args:
            response: Response to be rendered
        """
        formatted_response = self.format_complex_response(response)
        self.console.print(formatted_response)
