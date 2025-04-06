from model.ContentLoader import ContentLoader
from model.PromptBuilder import PromptBuilder

class State():
    def __init__(self) -> None:
        self.content_loader: ContentLoader = ContentLoader()
        self.prompt_builder: PromptBuilder = PromptBuilder()
        self.unsent_prompt: str = ''
        self.chat_history: list = []
        self.displayed_chat_history: list = []
        self.refresh_chat: function = None
        self.clear_uploads: function = None