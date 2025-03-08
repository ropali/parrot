from dataclasses import dataclass


@dataclass
class AgentResponse:
    content: str
    error: str
    raw_input: str
