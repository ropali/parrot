from parrot.agents.factory import AgentsFactory
from parrot.config import ProviderConfig
from parrot.models import ModelLoader
from parrot.prompter import ConnectionPrompter, DataSourcePrompter
from parrot.interactive.chat_interface import ChatInterface


class Parrot:
    """
    Main class for the Parrot application, implementing the Facade design pattern to
    abstract interaction with models and agents.
    """

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.data_source_type = None

        self.agent = None

    def initialize_agent(self):
        """
        Initialize the agent based on the data source type.
        """
        self.data_source_type = DataSourcePrompter().prompt()

        model = ModelLoader.load(self.config.provider, self.config.model, self.config.api_key)

        conn_prompter = ConnectionPrompter()

        conn_details = conn_prompter.prompt(source_type=self.data_source_type)

        self.agent = AgentsFactory().create(model, conn_details)

    def run(self):
        """
        Launch the Textual-based chat interface.
        """

        self.initialize_agent()

        if not self.agent:
            raise ValueError("Agent is not initialized.")

        app = ChatInterface()
        app.run(self.agent)
