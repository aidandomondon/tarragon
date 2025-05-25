from typing import Sequence
from textwrap import dedent
from model.Embeddor import Embeddor
from json import loads
from nicegui.ui import notification
from model.DbClient import DbClient

with open('./config.json', 'r') as file:
    config = loads(file.read())

class PromptBuilder():

    def __init__(self, db_client: DbClient):
        self.db_client = db_client


    def _embed_query(self, query: str) -> Sequence[float]:
        processing_question_notifier = notification('Processing question...')
        processing_question_notifier.spinner = True
        response: Sequence[float] = Embeddor().__call__(query)
        processing_question_notifier.dismiss()
        return response

    def _retrieve_similar_chunks(self, query: str) -> list[str]:
        """
        Search for the given embedding in the vector db.
        """
        try:

            # Search for 5 documents closest to query.
            # Note: may have to make async and display waiting message for UX
            # if querying takes a long time.
            search_notifier = notification("Searching documents for relevant info...")
            search_notifier.spinner = True
            query_result = self.db_client.db_collection.query(
                query_texts=[query],
                n_results=5,
                include=["metadatas", "distances"]
            )
            results = query_result
            search_notifier.dismiss()
            # sort by vector distance
            print("RESULTS: \n\n")
            print(results)

            # Transform results into the expected format
            top_results = [metadata['chunk'] for metadata in results['metadatas'][0]][:config["search"]["top_k"]]
            return top_results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _build_context(self, query: str) -> str:
        similar_chunks = self._retrieve_similar_chunks(query)
        context_string = ""
        for i, embedding in enumerate(similar_chunks):
            context_string += f"\nDocument {i+1}:\n{embedding}\n"
        print(f"Context String: {context_string}")
        return context_string

    def build_prompt(self, query: str) -> str:
        context = self._build_context(query)
        prompt = dedent(f"""\
                            You are a helpful AI assistant. 
                            Use the following context to answer the query as accurately as possible. If the context is 
                            not relevant to the query, say 'I don't know'.

                            Context:
                            {context}

                            Query: {query}

                            Answer:""")
        return prompt