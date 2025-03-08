from abc import ABC, abstractmethod
from typing import List
from agents.filters import TextFilter
from agents.response import AgentResponse
from phi.model.base import Model


class ParrotAgent(ABC):

    def __init__(
        self,
        model: Model,
        input_filters: List[TextFilter] = None,
        output_filters: List[TextFilter] = None,
    ):
        self.model = model
        self.input_filters = input_filters if input_filters else []
        self.output_filters = output_filters if output_filters else []

    @abstractmethod
    def run(self, input_text: str) -> AgentResponse:
        pass
