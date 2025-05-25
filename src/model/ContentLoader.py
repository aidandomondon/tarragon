from json import loads
from model.Embeddor import Embeddor
from typing import Sequence
import pymupdf
from model.DbClient import DbClient

with open('./config.json', 'r') as file:
    config = loads(file.read())

class ContentLoader:

    def __init__(self, db_client: DbClient) -> None:
        # Client for API of database used to store embeddings of content
        self.db_client = db_client
        self.chunk_size = 300
        self.chunk_overlap_size = 50


    # Returns a string of all text that appears in the given file
    @staticmethod
    def _extract_text(file: bytes, file_type: str) -> str:
        print("Extracting text from uploaded file...")
        if file_type == 'text/plain':
            return file.decode()
        elif file_type == 'application/pdf':
            doc = pymupdf.open(stream=file)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        else:
            raise Exception('Unsupported file type.')
        

    # Break the given text into chunks
    def _chunk(self, text: str) -> list[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap_size):
            chunk = " ".join(words[i : i + self.chunk_size])
            chunks.append(chunk)
        return chunks



    async def ingest(self, file_id: str, file: bytes, file_type: str):
        """
        Stores the given `file` in the assistant's records.
        """
        print("Storing file...")

        # Extract text from files
        file_text: str = ContentLoader._extract_text(file, file_type)
        
        # Break text into chunks
        chunks: list[str] = self._chunk(file_text)

        # Embed and store each chunk in the DB
        for chunk_num, chunk in enumerate(chunks):
            embedding_id = f"{file_id}_chunk_{chunk_num}"
            embedding: Sequence[float] = Embeddor().__call__(chunk)
            await self.db_client._store_embedding(embedding_id, embedding, chunk)