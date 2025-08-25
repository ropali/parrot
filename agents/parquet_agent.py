from phi.agent import Agent
from phi.model.base import Model
from phi.run.response import RunResponse
from phi.tools.duckdb import DuckDbTools
import pandas as pd
import logging

from agents.base_agent import ParrotAgent
from agents.prompts import DUCKDB_SYSTEM_PROMPT
from agents.response import AgentResponse

# Remove existing handlers from the 'phi' logger
phi_logger = logging.getLogger("phi")
phi_logger.handlers.clear()  # This removes all handlers including RichHandler
phi_logger.setLevel(logging.CRITICAL)  # Set to CRITICAL to suppress logs

# Ensure 'rich' logs are also suppressed
logging.getLogger("rich").setLevel(logging.CRITICAL)


class ParquetAgent(ParrotAgent):
    def __init__(self, model: Model, file_path: str) -> None:
        self.file_path = file_path
        self.model = model
        self._agent = None

        self.init_agent()

    def _prepare_prompt(self) -> str:
        df = pd.read_parquet(self.file_path)

        head = df.head().to_string(index=False)
        print(head)
        return DUCKDB_SYSTEM_PROMPT.replace("$HEAD", head)

    def init_agent(self) -> None:
        tool = DuckDbTools()
        table_name, _ = tool.load_local_path_to_table(self.file_path)
        self._agent = Agent(
            model=self.model,
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
            system_prompt=self._prepare_prompt(),
            tools=[tool],
            show_tool_calls=False,
            add_datetime_to_instructions=False,
            debug_mode=False,
        )

    def run(self, input_text: str) -> AgentResponse:
        response: RunResponse = self._agent.run(input_text)
        return AgentResponse(content=response.content, error=None, raw_input=input_text)
