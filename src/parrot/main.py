from parrot.rag.storage.bootstrap import init_db
import os
from typing import Optional

import typer
from rich.console import Console

from parrot.config import Config, ProviderConfig
from parrot.parrot import Parrot
from rich.text import Text
from rich.align import Align
from rich.table import Table


USER_DIR = os.path.expanduser("~/.parrot")
API_KEYS_FILE = os.path.join(USER_DIR, "api_keys.json")


def display_banner(console: Console, config: ProviderConfig) -> None:
    art = """
    ██████╗  █████╗ ██████╗ ██████╗  ██████╗ ████████╗
    ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝
    ██████╔╝███████║██████╔╝██████╔╝██║   ██║   ██║   
    ██╔═══╝ ██╔══██║██╔══██╗██╔══██╗██║   ██║   ██║   
    ██║     ██║  ██║██║  ██║██║  ██║╚██████╔╝   ██║   
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   
    """
    console.clear()

    console.print(Align.center(Text(art, style="bold cyan")))

    # Tagline
    console.print(
        Align.center(Text("Your Intelligent AI Companion", style="italic bright_white"))
    )

    console.print()
    console.print(Align.center(Text("━" * 54, style="dim cyan")))
    console.print(
        Align.center(
            Text(
                f"v1.0.0  •  Model: {config.model}  •  Provider: {config.provider}",
                style="dim white",
            )
        )
    )
    console.print(Align.center(Text("━" * 54, style="dim cyan")))
    console.print()

    # Quick-start hint bar
    hints = Table.grid(padding=(0, 3))
    hints.add_column(justify="center")
    hints.add_column(justify="center")
    hints.add_column(justify="center")
    hints.add_row(
        Text("💬  /chat", style="bright_cyan"),
        Text("🛠️   /tools", style="bright_cyan"),
        Text("❓  /help", style="bright_cyan"),
    )
    console.print(Align.center(hints))
    console.print()


def main(
    model_config: Optional[bool] = typer.Option(
        False, help="Model to use (e.g., gtp-40, sonet 3.5)"
    ),
    use_tui: bool = typer.Option(
        False, "--tui", help="Use the new Textual TUI interface"
    ),
):
    """
    Parrot: SQL Query Agent with Natural Language Interface
    """
    console = Console()
    config = Config()

    init_db()

    if model_config:
        provider_config = config.prompt()
    else:
        try:
            # Interactive connection params if not provided
            provider_config = config.load()
        except FileNotFoundError:
            provider_config = config.prompt()

    try:
        display_banner(console, provider_config)
        parrot = Parrot(provider_config, use_tui=use_tui)

        parrot.run()
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/]")
        raise typer.Abort()


if __name__ == "__main__":
    typer.run(main)
