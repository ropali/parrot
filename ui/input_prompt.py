from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import FormattedText


class InputPrompt:
    def __init__(self):
        self.session = PromptSession()


    def ask(self, prompt: str, placeholder: FormattedText) -> str:
        return self.session.prompt(prompt, placeholder=placeholder)