"""
SUMMARIZE AGENT
---------------
This is what fixes the "1-2 line summary" problem from your previous attempt.

Strategy: MAP-REDUCE
  MAP    → Summarize each chunk (or group of chunks) independently
  REDUCE → Combine all mini-summaries into one structured final summary

The LLM never sees the whole document at once (token limit).
Instead it sees: small piece → summarize → collect → final merge.

For large documents (many chunks), we group chunks before mapping
to reduce the number of API calls while keeping quality high.
"""


class SummarizeAgent:
    def __init__(self, groq_client):
        self.groq = groq_client

    # ------------------------------------------------------------------ #
    #  MAP: Summarize one group of chunks                                  #
    # ------------------------------------------------------------------ #
    def _summarize_group(self, text: str, group_index: int) -> str:
        """Summarize a single chunk-group. Used in the MAP phase."""
        try:
            resp = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a precise document analyst. "
                            "Read the text section and extract ALL key points, facts, "
                            "concepts, findings, figures mentioned, and conclusions. "
                            "Be thorough — do not skip anything important. "
                            "Write in clear bullet points."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Section {group_index + 1}:\n\n{text}",
                    },
                ],
                max_tokens=400,
                temperature=0.2,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"[Section {group_index + 1} — extraction failed: {e}]"

    # ------------------------------------------------------------------ #
    #  REDUCE: Combine all mini-summaries into final structured summary    #
    # ------------------------------------------------------------------ #
    def _final_reduce(self, mini_summaries: list, doc_name: str) -> str:
        """Combine all section bullet points into a final structured summary."""
        combined = "\n\n".join(
            [f"--- Section {i+1} ---\n{s}" for i, s in enumerate(mini_summaries)]
        )

        resp = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert document summarizer. "
                        "You will receive key points extracted from all sections of a document. "
                        "Your job is to write a comprehensive, well-structured, flowing summary.\n\n"
                        "Format your summary as follows:\n"
                        "1. **Overview** — What is this document about? (2-3 sentences)\n"
                        "2. **Main Topics Covered** — List the key subjects discussed\n"
                        "3. **Key Findings / Content** — Important details, data, concepts\n"
                        "4. **Conclusions / Takeaways** — What are the main conclusions or outcomes?\n\n"
                        "Write in clear paragraphs. Be thorough and detailed. "
                        "Do not skip important information from any section."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Here are the extracted key points from all sections of '{doc_name}':\n\n"
                        f"{combined}\n\n"
                        f"Now write a complete, detailed summary of this document."
                    ),
                },
            ],
            max_tokens=1800,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()

    # ------------------------------------------------------------------ #
    #  Main Entry Point                                                    #
    # ------------------------------------------------------------------ #
    def summarize(self, chunks: list, doc_name: str = "the document", progress_callback=None) -> str:
        """
        Full map-reduce summarization.

        Groups chunks to reduce API calls:
          < 10 chunks  → each chunk individually
          10-30 chunks → groups of 2
          > 30 chunks  → groups of 3
        """
        if not chunks:
            return "No content found to summarize."

        # Decide grouping
        n = len(chunks)
        if n <= 10:
            group_size = 1
        elif n <= 30:
            group_size = 2
        else:
            group_size = 3

        # Build groups
        groups = []
        for i in range(0, n, group_size):
            group_text = "\n\n".join(chunks[i : i + group_size])
            if len(group_text.strip()) > 50:
                groups.append(group_text)

        total = len(groups)
        if progress_callback:
            progress_callback(f"📊 Summarizing {total} sections (MAP phase)...")

        # MAP phase
        mini_summaries = []
        for idx, group in enumerate(groups):
            if progress_callback:
                progress_callback(f"📝 Processing section {idx + 1} of {total}...")
            summary = self._summarize_group(group, idx)
            mini_summaries.append(summary)

        # REDUCE phase
        if progress_callback:
            progress_callback("🔗 Combining into final summary (REDUCE phase)...")

        final = self._final_reduce(mini_summaries, doc_name)
        return final
