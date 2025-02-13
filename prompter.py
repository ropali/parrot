import functools
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Union, Dict, List, Any, Type

import httpx
import typer
from InquirerPy import inquirer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, \
    BarColumn
from rich.prompt import Prompt
from rich.style import Style

from exporter import ExportType


@dataclass
class SQLConnectionDetails:
    user: str
    password: str
    host: str
    port: str
    database: str

    def to_connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class CSVConnectionDetails:
    file_path: str

    def __post_init__(self):

        if not self.file_path:
            raise typer.Abort("File path cannot be empty.")

        if self.file_path.startswith(("http://", "https://")):
            self.file_path = self._download_file()

    def _download_file(self):
        console = Console()

        with Progress(
                SpinnerColumn(style="dots2"),
                TextColumn("[progress.description]{task.description}",
                           style=Style(color=typer.colors.WHITE, italic=True)),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
                console=console,
                transient=True
        ) as progress:
            try:

                with httpx.Client(follow_redirects=True) as client:

                    with client.stream("GET", self.file_path, timeout=10.0) as response:
                        response.raise_for_status()
                        total_size = int(response.headers.get('content-length', 0))
                        task = progress.add_task(description="Downloading..", total=total_size or 1)

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
                            for chunk in response.iter_bytes(chunk_size=1024):
                                temp_file.write(chunk)
                                progress.update(task, advance=len(chunk))

                            return temp_file.name

            except httpx.RequestError as e:
                print(f"Network error occurred: {e}")
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise typer.Exit(code=1)

            raise typer.Exit()


# TODO: Explore Python's Protocol to enforce a common interface for connection details
ConnectionDetails = Union[SQLConnectionDetails, CSVConnectionDetails]


class ConnectionPrompter:
    """
    Class responsible for prompting the user for connection details based on the data source type.
    """

    def prompt(self, source_type: str) -> ConnectionDetails:
        if source_type == "sql":
            return self.get_sql_connection_details()
        elif source_type == "csv":
            return self.get_csv_file_path()
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")

    def get_sql_connection_details(self) -> SQLConnectionDetails:
        # TODO: Remove hardcoded defaults
        # TODO: test the connection before returning
        return SQLConnectionDetails(
            user=Prompt.ask("[blue]Database user[/]", default="postgres"),
            password=Prompt.ask("[blue]Database password[/]", password=False, default="mysecretpassword"),
            host=Prompt.ask("[blue]Database host[/]", default="172.17.0.4"),
            port=Prompt.ask("[blue]Database port[/]", default="5432"),
            database=Prompt.ask("[blue]Database name[/]", default="netflix")
        )

    def get_csv_file_path(self) -> CSVConnectionDetails:
        return CSVConnectionDetails(
            file_path=Prompt.ask("[blue]Enter the path to the CSV file[/]")
        )


class DataSourcePrompter:
    """
    Class responsible for prompting the user to select a data source type.
    """

    def prompt(self) -> str:
        data_source_type = inquirer.select(
            message="Select data source type:",
            choices=["SQL", "CSV"],
            default="SQL",

        ).execute()

        return data_source_type.lower()


class ConfigPrompter:
    """
    A flexible configuration prompter that dynamically handles different provider configurations
    based on a template structure.
    """

    def __init__(self):
        self.template = json.loads(Path("llms.json").read_text())

        self.required_fields = {
            "api_key": self._prompt_api_key,
            "endpoint": self._prompt_endpoint
        }

    def prompt(self) -> Dict[str, Prompt]:
        """
        Main method to handle the configuration flow.

        Returns:
            Dict containing the collected configuration
        """
        # Select provider
        selected_provider = self._prompt_provider(self.template.keys())
        provider_config = self.template[selected_provider]

        # Initialize result with selected provider
        prompts = {
            "provider": selected_provider,
        }

        # Handle model selection if models exist
        if provider_config.get("models"):
            models = [m["name"] for m in provider_config["models"]]
            if models:
                prompts["model"] = self._prompt_model(models)

        # Dynamically prompt for all required fields in the provider's config
        for field, value in provider_config.items():
            if field != "models" and field in self.required_fields:
                prompts[field] = self.required_fields[field]()
            elif field != "models" and value is not None:
                prompts[field] = value

        return prompts

    def _prompt_provider(self, providers: List[str]) -> str:
        """Prompt for LLM provider selection."""
        return inquirer.select(
            message="Select a LLM provider:",
            choices=providers,
            transformer=lambda result: result.title()
        ).execute()

    def _prompt_model(self, models: List[str]) -> str:
        """Prompt for model selection."""
        return inquirer.select(
            message="Select a model:",
            choices=models,
            transformer=lambda result: result.title()
        ).execute()

    def _prompt_api_key(self, default: str = None) -> str:
        """Prompt for API key."""
        return Prompt.ask("Enter your API key", default=default)

    def _prompt_endpoint(self, default: str = None) -> str:
        """Prompt for endpoint URL."""
        return Prompt.ask("Enter the endpoint URL", default=default)

    def add_field_prompt(self, field_name: str, prompt_func: callable, default: str = None):
        """
        Add a new field prompt handler.

        Args:
            field_name: Name of the field in the template
            prompt_func: Function that handles prompting for this field
            default: Default value for the field
        """
        self.required_fields[field_name] = functools.partial(prompt_func, default=default)


class ExportPrompter:
    """
    Class responsible for prompting the user to select a export type.
    """

    def prompt(self) -> Tuple[ExportType, str]:
        export_type = inquirer.select(
            message="Select export type:",
            choices=["TEXT", "JSON", "CSV"],
            default="TEXT",

        ).execute()

        export_type = ExportType[export_type]

        # Ask file path
        file_path = Prompt.ask("Enter the export file path")


        return export_type, file_path