from dataclasses import dataclass
from typing import Union

from InquirerPy import inquirer
from rich.prompt import Prompt


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