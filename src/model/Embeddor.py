from json import loads
from requests import request
from chromadb.api.types import EmbeddingFunction, Embeddings

with open('./config.json') as file:
    config = loads(file.read())

class Embeddor(EmbeddingFunction[list[str]]):

    def __init__(self):
        self.a = 'a'
        
    def embed(self, input: str) -> list[float]:
        response = request(
            method = 'POST',
            url = f"http://localhost:{config["embedding"]["model_port"]}/embedding",
            data = {
                "content": input
            }
        )
        return response.json()["embedding"]
    
    def __call__(self, input: str):
        return self.embed(input)