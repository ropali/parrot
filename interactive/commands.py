from abc import abstractmethod, ABC
from dataclasses import dataclass
from enum import auto, Enum
from typing import Optional, Any

from rich.text import Text

from exporter import Exporter
from interactive.help.help_display import HelpDisplay
from prompter import ExportPrompter


class CommandResult(Enum):
    CONTINUE = auto()  # Continue processing
    STOP = auto()  # Stop the application
    SKIP = auto()  # Skip to next iteration


@dataclass
class CommandResponse:
    result: CommandResult
    data: Optional[Any] = None


class Command(ABC):
    @abstractmethod
    def execute(self, interface: 'ChatInterface') -> CommandResponse:
        pass


class QuitCommand(Command):
    def execute(self, interface: 'ChatInterface') -> CommandResponse:
        return CommandResponse(CommandResult.STOP)


class HelpCommand(Command):
    def execute(self, interface: 'ChatInterface') -> CommandResponse:
        help_display = HelpDisplay(interface.console)
        help_display.display_help()
        return CommandResponse(CommandResult.SKIP)


class ExportCommand(Command):
    def execute(self, interface: 'ChatInterface') -> CommandResponse:
        export_type, file_path = ExportPrompter().prompt()
        exporter = Exporter(interface.chat_history)
        exporter.export(export_type, file_path)
        interface.display_message(Text("Export completed.", style="italic dim"))
        return CommandResponse(CommandResult.SKIP)