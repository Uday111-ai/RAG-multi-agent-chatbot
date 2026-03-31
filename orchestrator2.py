"""
ORCHESTRATOR
------------
The brain of the system. Coordinates all 5 agents.

Flow for document upload:
  IngestionAgent → parse + chunk + embed + store

Flow for each query:
  IntentAgent → detect what user wants
       ↓
  "summarize"?   → SummarizeAgent (map-reduce, NO search)
  anything else? → RetrievalAgent (semantic search)
       ↓
  Score check → filter bad retrievals
       ↓
  AnswerAgent → generate grounded response

One instance of the Orchestrator holds:
  - shared SentenceTransformer (loaded once into RAM)
  - shared ChromaDB client
  - all 5 agents
  - current document state
"""

import os
import re
import chromadb
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from agents.ingestion_agent  import IngestionAgent
from agents.intent_agent     import IntentAgent
from agents.retrieval_agent  import RetrievalAgent
from agents.summarize_agent  import SummarizeAgent
from agents.answer_agent     import AnswerAgent

load_dotenv()


class Orchestrator:
    def __init__(self, chroma_path: str = "./chroma_db"):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")

        # Shared resources (loaded once)
        self.embedder     = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.chroma       = chromadb.PersistentClient(path=chroma_path)
        self.groq_client  = Groq(api_key=api_key)

        # Agents
        self.ingestion_agent  = IngestionAgent(self.embedder, self.chroma)
        self.intent_agent     = IntentAgent(self.groq_client)
        self.retrieval_agent  = RetrievalAgent(self.embedder, self.chroma)
        self.summarize_agent  = SummarizeAgent(self.groq_client)
        self.answer_agent     = AnswerAgent(self.groq_client)

        # State
        self.current_collection = None
        self.current_doc_name   = None
        self.all_chunks         = []
        self.doc_metadata       = {}

    # ------------------------------------------------------------------ #
    #  Document loading                                                    #
    # ------------------------------------------------------------------ #
    def load_document(self, pdf_path: str, progress_callback=None) -> dict:
        """
        Ingest a new PDF.
        Returns metadata: num_pages, num_chunks.
        """
        # Sanitize filename → use as collection name
        raw_name = os.path.basename(pdf_path)
        doc_name = os.path.splitext(raw_name)[0]
        collection_name = re.sub(r"[^a-zA-Z0-9_-]", "_", doc_name)[:50]

        # Must be at least 3 chars for ChromaDB
        if len(collection_name) < 3:
            collection_name = "doc_" + collection_name

        result = self.ingestion_agent.ingest(
            pdf_path=pdf_path,
            collection_name=collection_name,
            progress_callback=progress_callback,
        )

        self.current_collection = collection_name
        self.current_doc_name   = doc_name
        self.all_chunks         = result["chunks"]
        self.doc_metadata       = {
            "num_pages":  result["num_pages"],
            "num_chunks": result["num_chunks"],
            "doc_name":   doc_name,
        }

        return self.doc_metadata

    # ------------------------------------------------------------------ #
    #  Query processing                                                    #
    # ------------------------------------------------------------------ #
    def query(self, user_query: str, progress_callback=None) -> dict:
        """
        Process a user query end-to-end.

        Returns a dict:
          answer        : the final answer string
          intent        : detected intent
          num_chunks    : how many chunks were used
          low_confidence: whether retrieval score was low
        """
        if not self.current_collection:
            return {
                "answer": "⚠️ Please upload a document first.",
                "intent": "none",
                "num_chunks": 0,
                "low_confidence": False,
            }

        # ── Step 1: Detect intent ──────────────────────────────────────
        if progress_callback:
            progress_callback("🔍 Detecting query intent...")
        intent = self.intent_agent.detect(user_query)

        # ── Step 2: Route ──────────────────────────────────────────────
        if intent == "summarize":
            if progress_callback:
                progress_callback("📚 Starting full document summarization...")
            answer = self.summarize_agent.summarize(
                chunks=self.all_chunks,
                doc_name=self.current_doc_name,
                progress_callback=progress_callback,
            )
            return {
                "answer": answer,
                "intent": intent,
                "num_chunks": len(self.all_chunks),
                "low_confidence": False,
            }

        # ── Step 3: Retrieve relevant chunks ───────────────────────────
        if progress_callback:
            progress_callback("🔎 Searching document for relevant sections...")

        retrieval_result = self.retrieval_agent.retrieve(
            query=user_query,
            collection_name=self.current_collection,
            intent=intent,
        )

        # retrieval_agent returns (chunks, score, low_confidence)
        if len(retrieval_result) == 3:
            chunks, score, low_confidence = retrieval_result
        else:
            chunks, score = retrieval_result
            low_confidence = False

        if chunks is None:
            return {
                "answer": (
                    "I couldn't find relevant information in the document "
                    "for your query. Please try rephrasing or ask something else."
                ),
                "intent": intent,
                "num_chunks": 0,
                "low_confidence": True,
            }

        # For figure/table: also do a targeted reference search
        if intent == "figure_table":
            extra = self.retrieval_agent.retrieve_by_reference(
                ref=user_query, collection_name=self.current_collection
            )
            # Merge, deduplicate
            seen = set(chunks)
            for e in extra:
                if e not in seen:
                    chunks.append(e)
                    seen.add(e)
            chunks = chunks[:10]

        # ── Step 4: Generate answer ─────────────────────────────────────
        if progress_callback:
            progress_callback("💬 Generating answer...")

        answer = self.answer_agent.answer(
            query=user_query,
            chunks=chunks,
            intent=intent,
            low_confidence=low_confidence,
        )

        return {
            "answer": answer,
            "intent": intent,
            "num_chunks": len(chunks),
            "low_confidence": low_confidence,
        }

    # ------------------------------------------------------------------ #
    def is_ready(self) -> bool:
        return self.current_collection is not None

    def get_doc_info(self) -> dict:
        return self.doc_metadata
