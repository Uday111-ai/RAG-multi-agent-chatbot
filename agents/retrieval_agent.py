"""
RETRIEVAL AGENT
---------------
Responsible for:
  - Embedding the user query (same model as ingestion — MUST match)
  - Searching ChromaDB for the most relevant chunks
  - Filtering out low-relevance results so LLM never gets garbage context
  - Special handling for figure/table queries (targets [SPECIAL] tagged chunks)
"""

import re


class RetrievalAgent:
    def __init__(self, embedder, chroma_client):
        self.embedder = embedder
        self.client = chroma_client

    # ------------------------------------------------------------------ #
    def retrieve(self, query: str, collection_name: str, intent: str, top_k: int = 8):
        """
        Retrieve the most relevant chunks for a query.

        For figure/table intents → boost top_k and prioritise [SPECIAL] tagged chunks.
        For factual intents      → use smaller top_k (precision over recall).
        For explain/general      → standard top_k.

        Returns: (list_of_chunks, best_score)
                 Returns (None, None) if nothing relevant found.
        """
        try:
            collection = self.client.get_collection(collection_name)
        except Exception:
            return None, None

        total_chunks = collection.count()
        if total_chunks == 0:
            return None, None

        # Adjust top_k per intent
        if intent == "figure_table":
            top_k = min(12, total_chunks)
        elif intent == "factual":
            top_k = min(5, total_chunks)
        else:
            top_k = min(top_k, total_chunks)

        # Embed the query
        query_embedding = self.embedder.encode([query]).tolist()

        # Query ChromaDB
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "distances"],
        )

        docs = results["documents"][0]
        distances = results["distances"][0]

        # Cosine distance: 0 = identical, 2 = opposite
        # We keep chunks with distance < 1.0 (reasonably relevant)
        THRESHOLD = 1.0

        filtered = [
            (doc, dist)
            for doc, dist in zip(docs, distances)
            if dist < THRESHOLD
        ]

        if not filtered:
            # Relax threshold — return best available but flag low confidence
            if docs:
                return docs[:3], distances[0], True   # low_confidence = True
            return None, None, True

        # For figure/table: push [SPECIAL] tagged chunks to the top
        if intent == "figure_table":
            special = [(d, s) for d, s in filtered if "[SPECIAL]" in d]
            others  = [(d, s) for d, s in filtered if "[SPECIAL]" not in d]
            filtered = special + others

        chunks = [doc for doc, _ in filtered]
        best_score = filtered[0][1]

        return chunks, best_score, False   # low_confidence = False

    # ------------------------------------------------------------------ #
    def retrieve_by_reference(self, ref: str, collection_name: str):
        """
        Targeted retrieval for things like 'Fig. 3' or 'Table 2'.
        Searches for exact reference in the stored chunks.
        Used as a supplement to semantic search.
        """
        try:
            collection = self.client.get_collection(collection_name)
            all_docs = collection.get(include=["documents"])["documents"]
        except Exception:
            return []

        pattern = re.compile(re.escape(ref), re.IGNORECASE)
        matched = [doc for doc in all_docs if pattern.search(doc)]
        return matched[:5]
