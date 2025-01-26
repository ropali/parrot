import os
import json
from typing import Optional, Dict

import typer
from rich.console import Console
from rich.prompt import Prompt

from parrot import Parrot

USER_DIR = os.path.expanduser("~/.parrot")
API_KEYS_FILE = os.path.join(USER_DIR, "api_keys.json")


def get_model_config() -> Dict[str, str]:
    console = Console()
    console.print("[bold blue]Interactive Model Configuration[/]")

    return {
        'model': Prompt.ask("Model Name", default="gtp-40"),
        'api_key': Prompt.ask("API Key")
    }

def load_api_keys() -> Dict[str, str]:
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_api_keys(api_keys: Dict[str, str]):
    os.makedirs(USER_DIR, exist_ok=True)
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(api_keys, f)

def main(
        model: Optional[str] = typer.Option(None, help="Model to use (e.g., gtp-40, sonet 3.5)"),
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
):
    """
    Parrot: SQL Query Agent with Natural Language Interface
    """
    console = Console()
    api_keys = load_api_keys()

    if model:
        if model not in api_keys:
            api_key = Prompt.ask(f"API Key for {model}")
            api_keys[model] = api_key
            save_api_keys(api_keys)
    else:
        if api_keys:
            model = list(api_keys.keys())[0]
        else:
            model_config = get_model_config()
            model = model_config["model"]
            save_api_keys({model: model_config["api_key"]})
            api_keys = load_api_keys()


    api_key = api_keys[model]

    # Interactive connection params if not provided

    try:
        parrot = Parrot(api_key=api_key, model_name=model)

        parrot.interactive_query()
    except Exception as e:
        console.print(f"[bold red]Connection Error: {e}[/]")
        raise typer.Abort()

if __name__ == "__main__":
    typer.run(main)