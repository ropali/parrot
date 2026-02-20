from phi.agent import Agent
from phi.model.base import Model
from phi.run.response import RunResponse
from phi.tools.sql import SQLTools



class SQLAgent:
    def __init__(self, model: Model, connection_string: str = None):
        self._agent = Agent(
            model=model,
            markdown=False,
            description="You are a data analyst.",
            instructions=[
                "For a given, search through the database schema to find out the tables to use.",
                "Then convert the natural language query into a SQL query.",
                "Analyse and execute the SQL query to answer the question.",
                "Figure the out table names and column names to use in the query.",
                "Don't add any additional information. Just answer the question.",
                "If you can't answer the question, just say 'I don't know'.",
            ],
            tools=[SQLTools(db_url=connection_string)],
            show_tool_calls=False,
            add_datetime_to_instructions=False,
            debug_mode=False
        )

    def run(self, input_text: str) -> RunResponse:
        return self._agent.run(input_text)
