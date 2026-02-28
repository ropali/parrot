from typing import Any

from phi.model.base import Model
from phi.model.groq import Groq
from phi.model.ollama import Ollama


class LLMModelLoader:
    """
    Class responsible for loading different models based on the model name.
    """

    @staticmethod
    def load(provider: str, model_name: str, api_key: str) -> Model:
        if provider.lower() == "groq":
            return Groq(id=model_name, api_key=api_key)
        elif provider.lower() == "ollama":
            return Ollama(id=model_name)
        else:
            raise ValueError(f"Unsupported model: {provider}")
