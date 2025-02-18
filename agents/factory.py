from typing import Any

import pandas as pd
from phi.model.base import Model

from agents.csv_agent import CSVAgent
from agents.sql_agent import SQLAgent
from prompter import ConnectionDetails, SQLConnectionDetails, CSVConnectionDetails
from agents.parquet_agent import ParquetAgent
from prompter import ParquetConnectionDetails


class AgentsFactory:
    """
    Factory class to initialize the correct agent based on the data source type.
    """
    def create(self, model: Model, connection_details: ConnectionDetails):
        if isinstance(connection_details, SQLConnectionDetails):
            return self.create_sql_agent(model, connection_details.to_connection_string())
        elif isinstance(connection_details, CSVConnectionDetails):
            return self.create_csv_agent(model, connection_details.file_path)
        elif isinstance(connection_details, ParquetConnectionDetails):
            return self.create_parquet_agent(model, connection_details.file_path)
        else:
            raise ValueError(f"Unsupported agent type: {model}")


    def create_sql_agent(self, model: Model, connection_string) -> Any:
        return SQLAgent(
            model=model,
            connection_string=connection_string
        )


    def create_csv_agent(self, model: Model, file_path: str) -> Any:

        return CSVAgent(
            model=model,
            file_path=file_path
        )

    def create_parquet_agent(self, model: Model, file_path: str) -> Any:
        return ParquetAgent(
            model=model,
            file_path=file_path
        )
