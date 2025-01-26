from typing import Any

from InquirerPy import inquirer
from phi.model.groq import Groq
from rich.prompt import Prompt

from agents.sql_agent import SQLAgent
from ui.chat_interface import ChatInterface


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
        self.data_source_type = self._get_data_source_type()

        model = ModelLoader.load_model(self.model_name, self.api_key)

        if self.data_source_type == "sql":
            connection_string = ConnectionPrompter.get_sql_connection_details()
            self.agent = AgentFactory.create_sql_agent(model, connection_string)
        elif self.data_source_type == "csv":
            file_path = ConnectionPrompter.get_csv_file_path()
            self.agent = AgentFactory.create_csv_agent(model, file_path)

    def run_interface(self):
        """
        Launch the Textual-based chat interface.
        """
        if not self.agent:
            raise ValueError("Agent is not initialized.")

        app = ChatInterface(self.agent, data_source_type=self.data_source_type)
        app.run()

# Example usage
if __name__ == "__main__":
    parrot = Parrot(api_key="your_api_key", model_name="groq")
    parrot.initialize_agent()
    parrot.run_interface()
