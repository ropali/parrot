from phi.agent import Agent
from phi.model.base import Model
from phi.run.response import RunResponse
from phi.tools.duckdb import DuckDbTools

import logging

# Remove existing handlers from the 'phi' logger
phi_logger = logging.getLogger("phi")
phi_logger.handlers.clear()  # This removes all handlers including RichHandler
phi_logger.setLevel(logging.CRITICAL)  # Set to CRITICAL to suppress logs

# Ensure 'rich' logs are also suppressed
logging.getLogger("rich").setLevel(logging.CRITICAL)


class ParquetAgent:
    def __init__(self, model: Model, file_path: str):
        self._init_agent(model, file_path)

    def _init_agent(self, model, parquet_file):
        tool = DuckDbTools()
        table_name, _ = tool.load_local_path_to_table(parquet_file)
        self._agent = Agent(
            model=model,
            markdown=False,
            description="You are a data analyst.",
            instructions=[
                f"Use the table {table_name} to answer the question.",
                "Then convert the natural language query into a duckdb SQL query.",
                "Analyse and execute the SQL query to answer the question.",
                "Figure the out column names to use in the query.",
                "Don't add any additional information. Just answer the question.",
                "If you can't answer the question, just say 'I don't know'.",
            ],
            tools=[tool],
            show_tool_calls=False,
            add_datetime_to_instructions=False,
            debug_mode=False
        )

    def run(self, input_text: str) -> RunResponse:
        return self._agent.run(input_text)
