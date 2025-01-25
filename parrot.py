import os

from rich.console import Console
from typing import Dict, List, Any

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.sql import SQLTools
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text


class Parrot:
    def __init__(self, connection_params: Dict[str, str], model: str, api_key: str):
        self.connection_params = connection_params
        self.console = Console()
        os.environ["GROQ_API_KEY"] = api_key
        self.groq_client = Groq(api_key=api_key)

        connection_string = (
            f"postgresql://{connection_params['user']}:"
            f"{connection_params['password']}@"
            f"{connection_params['host']}:"
            f"{connection_params['port']}/"
            f"{connection_params['database']}"
        )

        self.agent = Agent(
            model=Groq(id="llama3-70b-8192"),
            markdown=False,
            description="You are a data analyst.",
            instructions=[
                "For a given, search through the database schema to find out the tables to use.",
                "Then convert the natural language query into a SQL query.",
                "Analyse and execute the SQL query to answer the question.",
                "Figure the out table names and column names to use in the query.",
                "Don't add any additional information. Just answer the question.",
            ],
            tools=[SQLTools(db_url=connection_string)],
            show_tool_calls=False,
            add_datetime_to_instructions=False,
        )

    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        return self.agent.run(sql_query)

    def interactive_query(self):
        self.console.print(Panel.fit(
            "[bold green]🦜 Parrot: Talk to your data![/]",
            title="Interactive Mode",
            border_style="bold blue",
        ))

        chat_history = []

        while True:
            try:
                query = Prompt.ask("[green]Your natural language query[/]", default="exit")

                if query.lower() in ['exit', 'quit', 'q']:
                    break

                chat_history.append(Text(f"[bold green]User:[/] {query}"))

                results = self.execute_query(query)

                if results:
                    chat_history.append(Text(f"[bold blue]Parrot:[/] {results.content}"))
                else:
                    chat_history.append(Text("[bold yellow]Parrot:[/] No results found."))

                self.console.print(Panel.fit(
                    "\n".join(str(item) for item in chat_history),
                    title="Chat History",
                    border_style="bold blue"
                ))

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled.[/]")
                continue
            except Exception as e:
                self.console.print(f"[bold red]Error: {e}[/]")
