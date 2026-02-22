from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    content: str = Field(default="", description="Actual answer generted by the LLM")
    is_markedown_formatted: bool = Field(
        default=False, description="Set to true if the content contains markdown format"
    )
