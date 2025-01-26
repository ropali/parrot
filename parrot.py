from typing import Dict, List, Any

from InquirerPy import inquirer
from phi.model.groq import Groq
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from agents.sql_agent import SQLAgent


class ModelLoader:
    """
    Class responsible for loading different models based on the model name.
    """
    @staticmethod
    def load_model(model_name: str, api_key: str) -> Any:
        if model_name.lower() == "groq":
            return Groq(id="llama3-70b-8192", api_key=api_key)
        else:
            raise ValueError(f"Unsupported model: {model_name}")

class AgentFactory:
    """
    Factory class to initialize the correct agent based on the data source type.
    """
    @staticmethod
    def create_sql_agent(model: Any, connection_string: str) -> Any:
        return SQLAgent(
            model=model,
            connection_string=connection_string
        )

    @staticmethod
    def create_csv_agent(model: Any, file_path: str) -> Any:
        # Placeholder for CSV agent implementation
        raise NotImplementedError("CSVAgent is not implemented yet.")

class ConnectionPrompter:
    """
    Class responsible for prompting the user for connection details based on the data source type.
    """
    @staticmethod
    def get_sql_connection_details() -> str:
        user = Prompt.ask("[blue]Database user[/]", default="postgres")
        password = Prompt.ask("[blue]Database password[/]", password=False, default="mysecretpassword")
        host = Prompt.ask("[blue]Database host[/]", default="172.17.0.4")
        port = Prompt.ask("[blue]Database port[/]", default="5432")
        database = Prompt.ask("[blue]Database name[/]", default="netflix")

        return (
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )

    @staticmethod
    def get_csv_file_path() -> str:
        return Prompt.ask("[blue]Enter the path to the CSV file[/]")

class Parrot:
    """
    Main class for the Parrot application, implementing the Facade design pattern to
    abstract interaction with models and agents.
    """
    def __init__(self, api_key: str, model_name: str):
        self.console = Console()

        self.api_key = api_key
        self.model_name = model_name.lower()
        self.agent = None


    def _get_data_source_type(self) -> str:
        """
        Prompt the user to select a data source type using a list with arrow key navigation.
        """
        data_source_type = inquirer.select(
            message="Select data source type:",
            choices=["SQL", "CSV"],
            default="SQL",
        ).execute()
        return data_source_type.lower()

    def initialize_agent(self):
        """
        Initialize the agent based on the data source type.
        """
        data_source_type = self._get_data_source_type()

        model = ModelLoader.load_model(self.model_name, self.api_key)

        if data_source_type == "sql":
            connection_string = ConnectionPrompter.get_sql_connection_details()
            self.agent = AgentFactory.create_sql_agent(model, connection_string)
        elif data_source_type == "csv":
            file_path = ConnectionPrompter.get_csv_file_path()
            self.agent = AgentFactory.create_csv_agent(model, file_path)

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a query using the agent.
        """
        if not self.agent:
            raise ValueError("Agent is not initialized.")

        return self.agent.run(query)

    def interactive_query(self):
        """
        Start the interactive query mode, allowing users to input natural language queries.
        """
        self.console.print(Panel.fit(
            "[bold green]Parrot 🦜: Talk to your data![/]",
            title="Interactive Mode",
            border_style="bold blue",
        ))

        self.initialize_agent()

        chat_history = []

        while True:
            try:
                query = Prompt.ask("[green]Your natural language query[/]", default="exit")

                if query.lower() in ['exit', 'quit', 'q']:
                    break

                chat_history.append(Text(f"[bold green]User:[/] {query}"))

                results = self.execute_query(query)

                if results:
                    chat_history.append(Text(f"[bold blue]Parrot:[/] {results.content}"))
                else:
                    chat_history.append(Text("[bold yellow]Parrot:[/] No results found."))

                self.console.print(Panel.fit(
                    "\n".join(str(item) for item in chat_history),
                    title="Chat History",
                    border_style="bold blue"
                ))

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled.[/]")
                continue
            except Exception as e:
                self.console.print(f"[bold red]Error: {e}[/]")
