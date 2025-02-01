import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from prompter import ConfigPrompter

USER_DIR = os.path.expanduser("~/.parrot")

MODEL_CONFIG = os.path.join(USER_DIR, "model_config.json")


class ProviderConfig(BaseModel):
    """Complete configuration for a provider after prompting."""
    provider: str
    model: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None

    class Config:
        extra = "allow"  # Allows additional fields added via add_field_prompt

class Config:

    prompeter = ConfigPrompter()

    def prompt(self):
        """
        Prompt the user for model configuration.
        """
        console = Console()
        header = Panel(
            Text("⏳ Interactive Model Configuration", style="bold blue", justify="center"),
            style="blue",
            expand=True,
        )
        console.print(header)
        data = self.prompeter.prompt()
        provider_config = ProviderConfig(**data)

        self._save(provider_config)

        console.clear()

        return provider_config

    def load(self) -> ProviderConfig:
        """
        Load the model configuration from the file.
        """
        if os.path.exists(MODEL_CONFIG):
            with open(MODEL_CONFIG, 'r') as f:
                return ProviderConfig(**json.load(f))

        raise FileNotFoundError(f"Model configuration file not found at {USER_DIR}.")

    def _save(self, provider_config: ProviderConfig):
        """
        Save the model configuration to the file.
        """
        os.makedirs(USER_DIR, exist_ok=True)

        with open(MODEL_CONFIG, 'w') as f:
            json.dump(provider_config.model_dump(), f)