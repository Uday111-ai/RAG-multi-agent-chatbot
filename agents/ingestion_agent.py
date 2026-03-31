"""
INGESTION AGENT
--------------
Responsible for:
  - Parsing PDF files using PyMuPDF
  - Detecting figures, tables, and formulas by caption patterns
  - Chunking text with overlap so no idea is cut in half
  - Embedding chunks locally (no API cost)
  - Storing everything in ChromaDB on disk
"""

import fitz  # PyMuPDF
import re


class IngestionAgent:
    def __init__(self, embedder, chroma_client):
        self.embedder = embedder
        self.client = chroma_client

    # ------------------------------------------------------------------ #
    #  STEP 1 — Parse PDF                                                  #
    # ------------------------------------------------------------------ #
    def parse_pdf(self, pdf_path):
        """
        Extract text page by page.
        Also tag lines that look like figure / table / formula captions
        so retrieval can find them easily.
        """
        doc = fitz.open(pdf_path)
        pages = []

        # Patterns that identify special content
        special_patterns = re.compile(
            r"(fig(ure)?\.?\s*\d+|table\s*\d+|eq(uation)?\.?\s*\d+|formula\s*\d+)",
            re.IGNORECASE,
        )

        for page_num, page in enumerate(doc):
            raw_text = page.get_text()

            # Tag special lines so they're easier to retrieve
            tagged_lines = []
            for line in raw_text.splitlines():
                if special_patterns.search(line):
                    tagged_line = f"[SPECIAL] {line.strip()}"
                else:
                    tagged_line = line.strip()
                tagged_lines.append(tagged_line)

            cleaned = "\n".join(tagged_lines)
            pages.append({"page": page_num + 1, "text": cleaned})

        doc.close()
        return pages

    # ------------------------------------------------------------------ #
    #  STEP 2 — Chunk                                                      #
    # ------------------------------------------------------------------ #
    def chunk_text(self, pages, chunk_size=400, overlap=80):
        """
        Split the full document into overlapping word-level chunks.
        Overlap ensures an idea that spans a boundary isn't lost.

        chunk_size = 400 words  (~512 tokens — sweet spot)
        overlap    = 80  words  keeps boundary context
        """
        # Stitch all pages together, keeping page markers
        full_text = ""
        for p in pages:
            full_text += f"\n\n[Page {p['page']}]\n{p['text']}"

        words = full_text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            # Skip near-empty chunks
            if len(chunk_text.strip()) > 60:
                chunks.append(chunk_text)

            if end == len(words):
                break
            start += chunk_size - overlap

        return chunks

    # ------------------------------------------------------------------ #
    #  STEP 3 — Embed + Store                                              #
    # ------------------------------------------------------------------ #
    def ingest(self, pdf_path, collection_name, progress_callback=None):
        """
        Full pipeline: parse → chunk → embed → store in ChromaDB.
        Returns metadata dict so the orchestrator knows what was ingested.
        """

        # --- Parse ---
        if progress_callback:
            progress_callback("📄 Parsing PDF...")
        pages = self.parse_pdf(pdf_path)
        full_text = "\n".join([p["text"] for p in pages])

        # --- Chunk ---
        if progress_callback:
            progress_callback("✂️  Chunking text...")
        chunks = self.chunk_text(pages)

        # --- Wipe old collection for this doc (fresh ingest) ---
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass
        collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},   # cosine distance → better similarity
        )

        # --- Embed + Store in batches ---
        if progress_callback:
            progress_callback(f"🧠 Embedding {len(chunks)} chunks (local, no API cost)...")

        # Embed all chunks in one shot — SentenceTransformer handles batching internally
        all_embeddings = self.embedder.encode(
            chunks, show_progress_bar=False, batch_size=256
        ).tolist()

        # Store in ChromaDB in one large batch (faster than many small adds)
        CHROMA_BATCH = 500
        for i in range(0, len(chunks), CHROMA_BATCH):
            collection.add(
                documents=chunks[i : i + CHROMA_BATCH],
                embeddings=all_embeddings[i : i + CHROMA_BATCH],
                ids=[f"chunk_{j}" for j in range(i, i + len(chunks[i : i + CHROMA_BATCH]))],
            )

        if progress_callback:
            progress_callback("✅ Document ready!")

        return {
            "num_pages": len(pages),
            "num_chunks": len(chunks),
            "full_text": full_text,
            "chunks": chunks,
        }
