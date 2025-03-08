from phi.agent import Agent
from phi.model.base import Model
from phi.run.response import RunResponse
from phi.tools.csv_tools import CsvTools

import logging

from agents.base_agent import ParrotAgent
from agents.prompts import DUCKDB_SYSTEM_PROMPT

# Remove existing handlers from the 'phi' logger
phi_logger = logging.getLogger("phi")
phi_logger.handlers.clear()  # This removes all handlers including RichHandler
phi_logger.setLevel(logging.CRITICAL)  # Set to CRITICAL to suppress logs

# Ensure 'rich' logs are also suppressed
logging.getLogger("rich").setLevel(logging.CRITICAL)


class CSVAgent(ParrotAgent):
    def __init__(self, model: Model, file_path: str) -> None:
        self._agent = None
        self.file_path = file_path
        self.model = model

        self.init_agent()

    def init_agent(self) -> None:
        self._agent = Agent(
            model=self.model,
            markdown=False,
            instructions=[
                "First always get the list of files",
                "Then check the columns in the file",
                "Then run the query to answer the question",
            ],
            system_prompt=DUCKDB_SYSTEM_PROMPT,
            tools=[CsvTools(csvs=[self.file_path])],
            show_tool_calls=False,
            add_datetime_to_instructions=False,
            debug_mode=False,
        )

    def run(self, input_text: str) -> RunResponse:
        return self._agent.run(input_text)
