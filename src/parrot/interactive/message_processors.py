from typing import Protocol


# Strategy Pattern for Message Processing
class MessageProcessor(Protocol):
    def process(self, query: str) -> str:
        pass


class AgentMessageProcessor(MessageProcessor):
    def __init__(self, agent):
        self.agent = agent

    def process(self, query: str) -> str:
        try:
            result = self.agent.run(query)
            return result.content if hasattr(result, "content") else str(result)
        except Exception as e:
            return f"Error processing query: {str(e)}"