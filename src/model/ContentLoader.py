from json import loads
from ollama import Client, EmbedResponse
from typing import Sequence
from redis import Redis
config = loads('../../config.json')

class ContentLoader:

    def __init__(self):
        # Client for API of model used to embed content
        self.embedding_model_client: Client = Client('http://localhost:3000')
        # Client for API of database used to store embeddings of content
        self.db_client: Redis = Redis(host='localhost', db=0)

    # Returns a string of all text that appears in the given file
    @staticmethod
    def _extract_text(file: bytes, file_type: str) -> str:
        if file_type == 'text/plain':
            return file.decode()
        elif file_type == 'application/pdf':
            raise Exception('To-do: implement pdf ingestion')
        else:
            raise Exception('Unsupported file type.')
        
    # Generates a vector embedding of the given text 
    # with this ContentLoader's Ollama client.
    # Arguments:
    # (str) text: text to embed
    # Returns:
    # (Sequence[float]) vector embedding of the given text
    def _embed(self, text: str) -> Sequence[float]:
        response: EmbedResponse = self.embedding_model_client.embed(
            model=config['embedding_model'],
            input=text
        )
        embeddings: Sequence[Sequence[float]] = response.embeddings
        if len(embeddings) == 1:
            return embeddings[0]
        else:
            raise Exception(
                f'Received {len(embeddings)} from API. Expected exactly 1 embedding.')

    # Stores the given embedding in the database
    def _store_embedding(self, embedding: Sequence[float]) -> None:
        self.db_client

    def ingest(self, file: bytes, file_type: str):
        """
        Stores the given `file` in the assistant's records.
        """
        file_text: str = ContentLoader._extract_text(file, file_type)
        embedding: Sequence[float] = self._embed(file_text)
        self._store_embedding(embedding)