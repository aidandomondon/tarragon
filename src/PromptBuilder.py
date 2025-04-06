from typing import Sequence
from textwrap import dedent
from redis.asyncio import Redis
from redis.commands.search.query import Query
import numpy as np
from ollama import AsyncClient, EmbedResponse
from json import loads
from nicegui.ui import notification

with open('./config.json', 'r') as file:
    config = loads(file.read())

class PromptBuilder():

    def __init__(self):
        self.db_client = Redis(port=6380)
        self.embed_client = AsyncClient('http://localhost:11434')
        self.top_k = 3
        self.index_name = "embedding_index"

    async def embed_query(self, query: str) -> Sequence[float]:

        processing_question_notifier = notification('Processing question...')
        processing_question_notifier.spinner = True
        response: EmbedResponse = await self.embed_client.embed(
            model=config['embedding_model'],
            input=query
        )
        processing_question_notifier.dismiss()

        embeddings: Sequence[Sequence[float]] = response.embeddings
        if len(embeddings) == 1:
            return embeddings[0]
        else:
            raise Exception(
                f'Received {len(embeddings)} from API. Expected exactly 1 embedding.')

    async def retrieve_similar_chunks(self, query: str) -> list[str]:
        """
        Search for the given embedding in Redis.
        """
        # Embed query in vector space
        query_embedding: Sequence[float] = await self.embed_query(query)

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
            search_notifier = notification("Searching documents for relevant info...")
            search_notifier.spinner = True
            results = await self.db_client.ft(self.index_name).search(
                q, query_params={"vec": query_vector}
            )
            search_notifier.dismiss()

            # Transform results into the expected format
            top_results = [result.chunk for result in results.docs][:self.top_k]
            return top_results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    async def build_context(self, query: str) -> str:
        similar_chunks = await self.retrieve_similar_chunks(query)
        context_string = ""
        for i, embedding in enumerate(similar_chunks):
            context_string += f"\nDocument {i+1}:\n{embedding}\n"
        return context_string

    async def build_prompt(self, query: str) -> str:
        context = await self.build_context(query)
        prompt = dedent(f"""\
                            You are a helpful AI assistant. 
                            Use the following context to answer the query as accurately as possible. If the context is 
                            not relevant to the query, say 'I don't know'.

                            Context:
                            {context}

                            Query: {query}

                            Answer:""")
            
        return prompt