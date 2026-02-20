import os
from typing import Optional

import typer
from rich.console import Console

from parrot.config import Config
from parrot.parrot import Parrot

USER_DIR = os.path.expanduser("~/.parrot")
API_KEYS_FILE = os.path.join(USER_DIR, "api_keys.json")


def main(model_config: Optional[bool] = typer.Option(False, help="Model to use (e.g., gtp-40, sonet 3.5)")):
    """
    Parrot: SQL Query Agent with Natural Language Interface
    """
    console = Console()
    config = Config()

    if model_config:
        provider_config = config.prompt()
    else:
        try:
            # Interactive connection params if not provided
            provider_config = config.load()
        except FileNotFoundError:
            provider_config = config.prompt()

    try:
        parrot = Parrot(provider_config)

        parrot.run()
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/]")
        raise typer.Abort()


if __name__ == "__main__":
    typer.run(main)
