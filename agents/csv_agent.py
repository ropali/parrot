from phi.agent import Agent
from phi.model.base import Model
from phi.run.response import RunResponse
from phi.tools.csv_tools import CsvTools

import logging

# Remove existing handlers from the 'phi' logger
phi_logger = logging.getLogger("phi")
phi_logger.handlers.clear()  # This removes all handlers including RichHandler
phi_logger.setLevel(logging.CRITICAL)  # Set to CRITICAL to suppress logs

# Ensure 'rich' logs are also suppressed
logging.getLogger("rich").setLevel(logging.CRITICAL)


class CSVAgent:
    def __init__(self, model: Model, file_path: str):
        self._init_agent(model, file_path)

    def _init_agent(self, model, csv_file):
        self._agent = Agent(
            model=model,
            markdown=False,
            description="You are a data analyst.",
            instructions=[
                "First always get the list of files",
                "Then check the columns in the file",
                "Then run the query to answer the question",
                "If you can't answer the question, just say 'I don't know'.",
            ],
            tools=[CsvTools(csvs=[csv_file])],
            show_tool_calls=False,
            add_datetime_to_instructions=False,
            debug_mode=False
        )

    def run(self, input_text: str) -> RunResponse:
        return self._agent.run(input_text)
