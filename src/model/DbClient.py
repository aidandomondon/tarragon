from json import loads
from chromadb import PersistentClient
from model.Embeddor import Embeddor
from chromadb import PersistentClient
from chromadb.errors import NotFoundError
from model.Embeddor import Embeddor
from typing import Sequence


with open('./config.json', 'r') as file:
    config = loads(file.read())

class DbClient():
    """
    Handles interactions with the vector embeddings database.
    """

    def __init__(self) -> None:
        self.db_client = PersistentClient(config["embedding"]["db_path"])
        self._create_hnsw_index()
        self.db_collection = self.db_client.get_collection(
            name = config["embedding"]["collection_name"], 
            embedding_function = Embeddor()
        )
    
    def reinit_db_client(self) -> None:
        self.db_client = PersistentClient(config["embedding"]["db_path"])
        self.db_collection = self.db_client.get_collection(
            name = config["embedding"]["collection_name"], 
            embedding_function = Embeddor()
        )

    # Clear the embedding store
    def _clear_store(self):
        self.db_client.delete_collection(config["embedding"]["collection_name"])
    
    # Create an HNSW index in the DB if it does not already exist
    def _create_hnsw_index(self):
        self.db_client.create_collection(
            name = config["embedding"]["collection_name"],
            embedding_function = Embeddor(),
            configuration = {
                "space": config["search"]["distance_metric"]
            },
            get_or_create = True
        )

    def clean_and_reinit(self) -> None:
        # Clear vector db store
        self._clear_store()
        self._create_hnsw_index()

    # Stores the given embedding in the database
    async def _store_embedding(self, embedding_id: str, embedding: Sequence[float], chunk: str) -> None:
        print("Storing embedding...")
        collection = self.db_client.get_collection(
            name = config["embedding"]["collection_name"], 
            embedding_function = Embeddor()
        )
        collection.add(
            ids = embedding_id,
            embeddings=embedding,
            metadatas={
                "chunk": chunk
            }
        )