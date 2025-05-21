from model.ContentLoader import ContentLoader
from model.PromptBuilder import PromptBuilder
from model.DbClient import DbClient

class State():
    def __init__(self) -> None:
        self.db_client = DbClient()
        self.content_loader: ContentLoader = ContentLoader(self.db_client)
        self.prompt_builder: PromptBuilder = PromptBuilder(self.db_client)
        self.unsent_prompt: str = ''
        self.chat_history: list = []
        self.displayed_chat_history: list = []
        self.refresh_chat: function = None
        self.clear_uploads: function = None