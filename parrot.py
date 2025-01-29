from typing import Any

from InquirerPy import inquirer
from phi.model.groq import Groq
from rich.prompt import Prompt

from agents.factory import AgentsFactory
from agents.sql_agent import SQLAgent
from models import ModelLoader
from prompter import ConnectionPrompter, DataSourcePrompter
from ui.chat_interface import ChatInterface




class Parrot:
    """
    Main class for the Parrot application, implementing the Facade design pattern to
    abstract interaction with models and agents.
    """
    def __init__(self, api_key: str, model_name: str):

        self.data_source_type = None
        self.api_key = api_key
        self.model_name = model_name.lower()
        self.agent = None


    def initialize_agent(self):
        """
        Initialize the agent based on the data source type.
        """
        self.data_source_type = DataSourcePrompter().prompt()

        model = ModelLoader.load(self.model_name, self.api_key)

        conn_prompter = ConnectionPrompter()

        conn_details = conn_prompter.prompt(source_type=self.data_source_type)

        self.agent = AgentsFactory().create(model, conn_details)

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
