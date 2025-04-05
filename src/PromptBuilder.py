from typing import Sequence
from textwrap import dedent
from redis import Redis
from redis.commands.search.query import Query
import numpy as np
from ollama import Client, EmbedResponse
from json import loads

with open('./config.json', 'r') as file:
    config = loads(file.read())

class PromptBuilder():

    def __init__(self):
        self.db_client = Redis(port=6380)
        self.embed_client = Client('http://localhost:11434')
        self.top_k = 3
        self.index_name = "embedding_index"

    def embed_query(self, query: str) -> Sequence[float]:
        print("Embedding query...")
        response: EmbedResponse = self.embed_client.embed(
            model=config['embedding_model'],
            input=query
        )
        embeddings: Sequence[Sequence[float]] = response.embeddings
        if len(embeddings) == 1:
            return embeddings[0]
        else:
            raise Exception(
                f'Received {len(embeddings)} from API. Expected exactly 1 embedding.')

    def retrieve_similar_chunks(self, query: str) -> list[str]:
        """
        Search for the given embedding in Redis.
        """
        print("Searching for matching documents...")
        # Embed query in vector space
        query_embedding: Sequence[float] = self.embed_query(query)

        # Convert embedding to bytes for Redis search
        query_vector = np.array(query_embedding, dtype=np.float32).tobytes()

        try:
            # Construct the vector similarity search query
            # Use a more standard RediSearch vector search syntax
            # q = Query("*").sort_by("embedding", query_vector)

            q = (
                Query("*=>[KNN 5 @embedding $vec AS vector_distance]")
                .sort_by("vector_distance")
                .return_fields("chunk", "vector_distance")
                .dialect(2)
            )

            # Perform the search
            results = self.db_client.ft(self.index_name).search(
                q, query_params={"vec": query_vector}
            )

            # Transform results into the expected format
            top_results = [result.chunk for result in results.docs][:self.top_k]
            return top_results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def build_context(self, query: str) -> str:
        similar_chunks = self.retrieve_similar_chunks(query)
        context_string = ""
        for i, embedding in enumerate(similar_chunks):
            context_string += f"\nDocument {i+1}:\n{embedding}\n"
        return context_string

    def build_prompt(self, query: str) -> str:
        context = self.build_context(query)
        prompt = dedent(f"""\
                            You are a helpful AI assistant. 
                            Use the following context to answer the query as accurately as possible. If the context is 
                            not relevant to the query, say 'I don't know'.

                            Context:
                            {context}

                            Query: {query}

                            Answer:""")
            
        return prompt