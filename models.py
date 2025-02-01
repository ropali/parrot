from typing import Any

from phi.model.base import Model
from phi.model.groq import Groq


class ModelLoader:
    """
    Class responsible for loading different models based on the model name.
    """

    @staticmethod
    def load(provider: str, model_name: str, api_key: str) -> Model:
        if provider.lower() == "groq":
            return Groq(id=model_name, api_key=api_key)
        else:
            raise ValueError(f"Unsupported model: {provider}")
