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

        # Conversation memory — stores last N turns
        self.conversation_memory = []   # list of {"role": "user"/"assistant", "content": "..."}
        self.MEMORY_TURNS = 6           # keep last 6 turns (3 Q&A pairs)

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

        # Clear memory when new document is loaded
        self.conversation_memory = []

        return self.doc_metadata

    def _resolve_query_with_memory(self, user_query: str) -> str:
        """
        If the user says something like 'explain more', 'what about step 2',
        'can you elaborate', etc. — resolve it into a full standalone question
        using conversation history. This way retrieval works correctly.
        """
        if not self.conversation_memory:
            return user_query

        # Keywords that indicate a follow-up question
        followup_signals = re.compile(
            r"^(explain more|elaborate|tell me more|what about|"
            r"and what|can you|more detail|go deeper|expand on|"
            r"what does that mean|give me more|continue|"
            r"what about (step|point|part|section)|"
            r"(what|how) (about|is) (it|this|that)|"
            r"more (about|on)|also|additionally)\b",
            re.IGNORECASE,
        )

        if not followup_signals.match(user_query.strip()):
            return user_query  # not a follow-up, use as-is

        # Ask LLM to resolve the ambiguous query using memory
        try:
            last_exchange = self.conversation_memory[-2:]  # last Q&A
            history_text = "\n".join(
                [f"{m['role'].upper()}: {m['content'][:300]}" for m in last_exchange]
            )
            resp = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Given the conversation history and a follow-up question, "
                            "rewrite the follow-up as a complete standalone question. "
                            "Return ONLY the rewritten question. Nothing else."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"History:\n{history_text}\n\nFollow-up: {user_query}\n\nRewritten question:",
                    },
                ],
                max_tokens=80,
                temperature=0,
            )
            resolved = resp.choices[0].message.content.strip()
            return resolved if resolved else user_query
        except Exception:
            return user_query

    # ------------------------------------------------------------------ #
    #  Query processing                                                    #
    # ------------------------------------------------------------------ #
    def query(self, user_query: str, progress_callback=None) -> dict:
        """
        Process a user query end-to-end.
        Uses conversation memory for follow-up questions.
        """
        if not self.current_collection:
            return {
                "answer": "⚠️ Please upload a document first.",
                "intent": "none",
                "num_chunks": 0,
                "low_confidence": False,
            }

        # ── Step 1: Resolve follow-up queries using memory ─────────────
        if progress_callback:
            progress_callback("🔍 Detecting query intent...")
        resolved_query = self._resolve_query_with_memory(user_query)

        # ── Step 2: Detect intent ──────────────────────────────────────
        intent = self.intent_agent.detect(resolved_query)

        # ── Step 3: Route ──────────────────────────────────────────────
        if intent == "summarize":
            if progress_callback:
                progress_callback("📚 Starting full document summarization...")
            answer = self.summarize_agent.summarize(
                chunks=self.all_chunks,
                doc_name=self.current_doc_name,
                progress_callback=progress_callback,
            )
            self._update_memory(user_query, answer)
            return {
                "answer": answer,
                "intent": intent,
                "num_chunks": len(self.all_chunks),
                "low_confidence": False,
            }

        # ── Step 4: Retrieve relevant chunks ───────────────────────────
        if progress_callback:
            progress_callback("🔎 Searching document for relevant sections...")

        retrieval_result = self.retrieval_agent.retrieve(
            query=resolved_query,
            collection_name=self.current_collection,
            intent=intent,
        )

        if len(retrieval_result) == 3:
            chunks, score, low_confidence = retrieval_result
        else:
            chunks, score = retrieval_result
            low_confidence = False

        if chunks is None:
            answer = (
                "I couldn't find relevant information in the document "
                "for your query. Please try rephrasing or ask something else."
            )
            self._update_memory(user_query, answer)
            return {
                "answer": answer,
                "intent": intent,
                "num_chunks": 0,
                "low_confidence": True,
            }

        # For figure/table: also do targeted reference search
        if intent == "figure_table":
            extra = self.retrieval_agent.retrieve_by_reference(
                ref=resolved_query, collection_name=self.current_collection
            )
            seen = set(chunks)
            for e in extra:
                if e not in seen:
                    chunks.append(e)
                    seen.add(e)
            chunks = chunks[:10]

        # ── Step 5: Generate answer with memory ────────────────────────
        if progress_callback:
            progress_callback("💬 Generating answer...")

        answer = self.answer_agent.answer(
            query=user_query,          # original query (not resolved) for natural response
            resolved_query=resolved_query,
            chunks=chunks,
            intent=intent,
            low_confidence=low_confidence,
            conversation_memory=self.conversation_memory,
        )

        self._update_memory(user_query, answer)

        return {
            "answer": answer,
            "intent": intent,
            "num_chunks": len(chunks),
            "low_confidence": low_confidence,
        }

    # ------------------------------------------------------------------ #
    def _update_memory(self, user_query: str, answer: str):
        """Add latest Q&A to memory, keep only last N turns."""
        self.conversation_memory.append({"role": "user",      "content": user_query})
        self.conversation_memory.append({"role": "assistant",  "content": answer[:800]})  # trim long answers
        # Keep only last MEMORY_TURNS messages
        if len(self.conversation_memory) > self.MEMORY_TURNS * 2:
            self.conversation_memory = self.conversation_memory[-(self.MEMORY_TURNS * 2):]

    def clear_memory(self):
        """Manually clear conversation memory."""
        self.conversation_memory = []
