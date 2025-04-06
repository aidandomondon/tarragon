from json import loads
from ollama import AsyncClient, EmbedResponse
from typing import Sequence
from redis.asyncio import Redis
from redis.exceptions import ResponseError
import numpy as np
import pymupdf

with open('./config.json', 'r') as file:
    config = loads(file.read())

class ContentLoader:

    def __init__(self) -> None:
        # Client for API of model used to embed content
        self.embedding_model_client: AsyncClient = AsyncClient(f"http://localhost:{config["ollama_port"]}")
        # Client for API of database used to store embeddings of content
        self.db_client: Redis = Redis(host='localhost', port=config['embedding']['db_port'], db=0)
        self.index_name = "embedding_index"     # Name of hash set in Redis db
        self.chunk_size = 300
        self.chunk_overlap_size = 50
        self.index_initialized = False


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
        

    # Generates a vector embedding of the given text 
    # with this ContentLoader's Ollama client.
    # Arguments:
    # (str) text: text to embed
    # Returns:
    # (Sequence[float]) vector embedding of the given text
    async def _embed(self, text: str) -> Sequence[float]:
        response: EmbedResponse = await self.embedding_model_client.embed(
            model=config['embedding']['model'],
            input=text
        )
        embeddings: Sequence[Sequence[float]] = response.embeddings
        if len(embeddings) == 1:
            return embeddings[0]
        else:
            raise Exception(
                f'Received {len(embeddings)} from API. Expected exactly 1 embedding.')


    async def clean_and_reinit(self) -> None:
        # Clear vector db store
        await self._clear_store()
        await self._create_hnsw_index()
        self.index_initialized = True


    # Clear the Redis store
    async def _clear_store(self):
        await self.db_client.flushall(asynchronous=False)


    # Create an HNSW index in Redis
    async def _create_hnsw_index(self):
        try:
            await self.db_client.execute_command(f"FT.DROPINDEX {self.index_name} DD")
        except ResponseError:
            pass    # index already does not exist

        await self.db_client.execute_command(
            f"""
            FT.CREATE {self.index_name} ON HASH
            SCHEMA text TEXT
            embedding VECTOR HNSW 6 DIM {config["embedding"]["dim"]} TYPE FLOAT32 DISTANCE_METRIC {config["search"]["distance_metric"]}
            """
        )


    # Stores the given embedding in the database
    async def _store_embedding(self, embedding_id: str, embedding: Sequence[float], chunk: str) -> None:
        print("Storing embedding...")
        await self.db_client.hset(
            name=embedding_id,
            mapping={
                "chunk": chunk,
                "embedding": np.array(embedding, dtype=np.float32).tobytes()  # Store as byte array
            }
        )


    async def ingest(self, file_id: str, file: bytes, file_type: str):
        """
        Stores the given `file` in the assistant's records.
        """
        print("Storing file...")
        # Initialize the index if not pre-existing
        if not self.index_initialized:
            await self.clean_and_reinit()

        # Extract text from files
        file_text: str = ContentLoader._extract_text(file, file_type)
        
        # Break text into chunks
        chunks: list[str] = self._chunk(file_text)

        # Embed and store each chunk in the DB
        for chunk_num, chunk in enumerate(chunks):
            embedding_id = f"{file_id}_chunk_{chunk_num}"
            embedding: Sequence[float] = await self._embed(chunk)
            await self._store_embedding(embedding_id, embedding, chunk)