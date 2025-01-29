from typing import Any

from phi.model.base import Model

from agents.sql_agent import SQLAgent
from prompter import ConnectionDetails, SQLConnectionDetails, CSVConnectionDetails


class AgentsFactory:
    """
    Factory class to initialize the correct agent based on the data source type.
    """
    def create(self, model: Model, connection_details: ConnectionDetails):
        if isinstance(connection_details, SQLConnectionDetails):
            return self.create_sql_agent(model, connection_details.to_connection_string())
        elif isinstance(connection_details, CSVConnectionDetails):
            return self.create_csv_agent(connection_details.file_path)
        else:
            raise ValueError(f"Unsupported agent type: {model}")


    def create_sql_agent(self, model: Model, connection_string) -> Any:
        return SQLAgent(
            model=model,
            connection_string=connection_string
        )


    def create_csv_agent(self, file_path: str) -> Any:
        # Placeholder for CSV agent implementation
        raise NotImplementedError("CSVAgent is not implemented yet.")