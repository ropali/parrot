import sys
from parrot.agents.factory import AgentsFactory
from parrot.config import ProviderConfig
from parrot.llm_loader import LLMModelLoader
from parrot.prompter import ConnectionPrompter, DataSourcePrompter
from parrot.tui.chat_tui import ChatTUI


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

        model = LLMModelLoader.load(
            self.config.provider, self.config.model, self.config.api_key
        )

        conn_prompter = ConnectionPrompter()
        conn_details = conn_prompter.prompt(source_type=self.data_source_type)

        self.agent = AgentsFactory().create(model, conn_details)
        return self.agent

    def run(self):
        """
        Launch the Textual TUI chat interface.
        """
        # Always use TUI, no main menu
        app = ChatTUI(
            agent=self.agent,
            config=self.config,
            parrot=self,
        )
        app.run()
