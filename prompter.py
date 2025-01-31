import tempfile
from dataclasses import dataclass
from typing import Union

import httpx
import typer
from InquirerPy import inquirer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, \
    BarColumn
from rich.prompt import Prompt
from rich.style import Style


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
