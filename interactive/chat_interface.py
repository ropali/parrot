from dataclasses import dataclass
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import typer
from phi.agent import Agent
from prompt_toolkit.formatted_text import FormattedText
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.style import Style
from rich.text import Text

from data_models import Conversation, Message
from interactive.chat_reponse import StyledChatResponse
from interactive.commands import QuitCommand, HelpCommand, ExportCommand, CommandResult, CommandResponse
from interactive.input_prompt import InputPrompt
from interactive.listeners import ChatEventListener
from interactive.message_processors import AgentMessageProcessor, MessageProcessor


# State Pattern for Chat Interface
class ChatState(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class ChatContext:
    state: ChatState = ChatState.IDLE
    last_error: Optional[str] = None


class ChatInterface:
    def __init__(self):
        self.console = Console()
        self.chat_styler = StyledChatResponse(self.console)
        self.chat_history = Conversation()
        self.context = ChatContext()
        self.message_processor: Optional[MessageProcessor] = None
        self.listeners: list[ChatEventListener] = []
        self.commands = {
            "/q": QuitCommand(),
            "/?": HelpCommand(),
            "/export": ExportCommand()
        }

    def set_message_processor(self, processor: MessageProcessor) -> None:
        self.message_processor = processor

    def add_listener(self, listener: ChatEventListener) -> None:
        self.listeners.append(listener)

    def remove_listener(self, listener: ChatEventListener) -> None:
        self.listeners.remove(listener)

    def notify_message_added(self, message: Message) -> None:
        for listener in self.listeners:
            listener.on_message_added(message)

    def add_message(self, message: str, sender: str) -> None:
        styled_message = self.chat_styler.create_message_text(message, sender)
        new_message = Message(sender, styled_message)
        self.chat_history.append(new_message)
        self.notify_message_added(new_message)

    def process_query(self, query: str) -> str:
        if not self.message_processor:
            raise ValueError("Message processor not set")

        self.context.state = ChatState.PROCESSING
        try:
            response = self.message_processor.process(query)
            self.context.state = ChatState.IDLE
            self.add_message(response, "Parrot")
            return response
        except Exception as e:
            self.context.state = ChatState.ERROR
            self.context.last_error = str(e)
            error_message = f"Error processing query: {str(e)}"
            self.add_message(error_message, "Error")
            return error_message

    def handle_command(self, cmd: str) -> CommandResponse:
        command_type = next((cmd_type for cmd_type in self.commands.keys()
                             if cmd.startswith(cmd_type)), None)

        if command_type:
            return self.commands[command_type].execute(self)

        return CommandResponse(CommandResult.CONTINUE)

    def run(self, agent: Agent) -> None:
        self.set_message_processor(AgentMessageProcessor(agent))

        self.display_header()

        while True:
            self.render_chat_history()

            try:
                user_query = InputPrompt().ask(
                    ">>> ",
                    FormattedText([
                        ("#949494 italic", "Ask your question (/? for help)"),
                    ])
                )

                if not user_query:
                    continue

                command_result = self.handle_command(user_query)

                match command_result.result:
                    case CommandResult.STOP:
                        break
                    case CommandResult.SKIP:
                        continue
                    case CommandResult.CONTINUE:
                        self.add_message(user_query, "You")
                        self._process_with_progress(user_query)

            except KeyboardInterrupt:
                break

        self._display_farewell()

    def _process_with_progress(self, query: str) -> None:
        with Progress(
                SpinnerColumn(style="dots2"),
                TextColumn(
                    "[progress.description]{task.description}",
                    style=Style(color=typer.colors.WHITE, italic=True),
                ),
                transient=True,
        ) as progress:
            progress.add_task(description="Processing...", total=None)
            self.process_query(query)

    def _display_farewell(self) -> None:
        self.console.print("[bold red]Goodbye! 👋[/]")

    def display_header(self) -> None:
        self.console.clear()
        header = Panel(
            Text("Parrot 🦜: Talk to your data!", style="bold cyan", justify="center"),
            style="blue",
            expand=True,
        )
        self.console.print(header)

    def render_chat_history(self) -> None:
        for message in self.chat_history:
            self.console.print(message.content)
