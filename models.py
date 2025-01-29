from typing import Any

from phi.model.base import Model
from phi.model.groq import Groq


class ModelLoader:
    """
    Class responsible for loading different models based on the model name.
    """
    @staticmethod
    def load(model_name: str, api_key: str) -> Model:
        if model_name.lower() == "groq":
            return Groq(id="llama3-70b-8192", api_key=api_key)
        else:
            raise ValueError(f"Unsupported model: {model_name}")