"""
ANSWER AGENT
------------
The final step in the pipeline — generates the actual response using Groq LLaMA.

Key features:
  - Different system prompts for each intent (explain, figure_table, factual, general)
  - Strictly grounded: LLM is FORBIDDEN from using outside knowledge
  - Length-controlled: answer length matches question complexity
  - Honest: says "not found" instead of hallucinating
"""


class AnswerAgent:
    def __init__(self, groq_client):
        self.groq = groq_client

    # ------------------------------------------------------------------ #
    #  System prompts per intent                                           #
    # ------------------------------------------------------------------ #
    PROMPTS = {
        "explain": {
            "system": """You are an expert document assistant helping a user understand their document.

STRICT RULES:
- Answer ONLY using the provided document context below
- NEVER use outside knowledge or make things up
- If the answer isn't clearly in the context, say: "This specific information isn't clearly covered in the provided sections of the document."

RESPONSE STYLE:
- Give a thorough, clear explanation (1-3 paragraphs depending on complexity)
- Use simple, accessible language
- If the document uses technical terms, explain them
- Structure your answer with a direct answer first, then elaboration
- Include specific details, examples, or data from the document""",
            "max_tokens": 900,
        },

        "figure_table": {
            "system": """You are an expert at interpreting technical content from academic and professional documents.

STRICT RULES:
- Explain ONLY using the provided document context
- NEVER guess or fabricate values, labels, or descriptions
- If the figure/table isn't described in the context, say so honestly

RESPONSE STYLE:
- First: state what the figure/table shows (1 sentence)
- Then: explain its purpose and significance (1 paragraph)
- Then: highlight key values, trends, relationships, or conclusions from it
- If it contains data: describe the patterns or findings
- Keep it clear — aim for 1-2 solid paragraphs""",
            "max_tokens": 700,
        },

        "factual": {
            "system": """You are a precise document assistant.

STRICT RULES:
- Answer with EXACT information from the document context
- NEVER guess or approximate
- If the fact is not in the context, say: "This specific fact is not found in the provided document sections."

RESPONSE STYLE:
- Be direct and concise (1-4 sentences)
- Lead with the answer immediately
- Quote specific numbers, names, or dates from the document if available""",
            "max_tokens": 250,
        },

        "table": {
            "system": """You are a data extraction and table generation expert.

STRICT RULES:
- Extract data ONLY from the provided document context
- NEVER invent or assume data not present in the context
- If insufficient data exists for a table, say so clearly

OUTPUT FORMAT — you MUST output a proper markdown table:
- Always include a header row with | Column | Column | format
- Separate header with |---|---|
- Every row must follow the same column structure
- Before the table, write 1 sentence explaining what the table shows
- After the table, write 1-2 sentences with key observations

Example format:
This table shows the comparison of methods described in the document.

| Method | Accuracy | Speed | Use Case |
|---|---|---|---|
| Method A | 95% | Fast | Classification |
| Method B | 89% | Slow | Detection |

Key observation: Method A offers higher accuracy while Method B is better suited for detection tasks.""",
            "max_tokens": 1000,
        },

        "diagram": {
            "system": """You are an expert at converting document content into Mermaid diagram code.

STRICT RULES:
- Base the diagram ONLY on content in the provided document context
- NEVER invent steps or connections not described in the document
- If the content cannot form a meaningful diagram, say so

OUTPUT FORMAT — you MUST output valid Mermaid code:
- Start with a brief 1-sentence description of what the diagram shows
- Then output the Mermaid code block
- Use graph TD for flowcharts (top-down)
- Use graph LR for pipelines (left-right)
- Keep node labels short (3-5 words max)
- Use --> for connections, -- label --> for labeled connections

Example format:
This diagram shows the data processing pipeline described in the document.

```mermaid
graph TD
    A[Data Collection] --> B[Preprocessing]
    B --> C{Quality Check}
    C -- Pass --> D[Model Training]
    C -- Fail --> B
    D --> E[Evaluation]
    E --> F[Deployment]
```

Supported shapes: [rectangle] (node), (rounded), {diamond} (decision), ([stadium])
Keep it clean — max 15 nodes for readability.""",
            "max_tokens": 800,
        },

        "general": {
            "system": """You are a helpful document assistant.

STRICT RULES:
- Answer ONLY from the provided document context
- Do NOT use outside knowledge
- If not found in context, say so clearly

RESPONSE STYLE:
- Match your answer length to the question:
    Simple question → 2-4 sentences
    Medium question → 1-2 paragraphs
    Complex question → up to 3 paragraphs
- Be clear, helpful, and grounded in the document""",
            "max_tokens": 700,
        },
    }

    # ------------------------------------------------------------------ #
    #  Main answer method                                                  #
    # ------------------------------------------------------------------ #
    def answer(self, query: str, resolved_query: str, chunks: list, intent: str,
               low_confidence: bool = False, conversation_memory: list = None) -> str:
        """
        Generate a grounded, intent-aware answer with conversation memory.
        """
        config = self.PROMPTS.get(intent, self.PROMPTS["general"])

        # Build document context
        context_parts = []
        for i, chunk in enumerate(chunks):
            clean_chunk = chunk.replace("[SPECIAL]", "").strip()
            context_parts.append(f"[Context {i+1}]\n{clean_chunk}")
        context = "\n\n".join(context_parts)

        # Build conversation history string for the prompt
        memory_text = ""
        if conversation_memory:
            history_lines = []
            for m in conversation_memory:
                role = "User" if m["role"] == "user" else "Assistant"
                # Trim each message to avoid bloating the prompt
                content = m["content"][:400] + ("..." if len(m["content"]) > 400 else "")
                history_lines.append(f"{role}: {content}")
            memory_text = "\n\nCONVERSATION HISTORY (for context only):\n" + "\n".join(history_lines)

        caveat = ""
        if low_confidence:
            caveat = (
                "\n\nNote: The most relevant sections were found, but the match confidence "
                "is lower than usual. Please verify critical details directly in your document."
            )

        try:
            resp = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": config["system"]},
                    {
                        "role": "user",
                        "content": (
                            f"DOCUMENT CONTEXT:\n{context}"
                            f"{memory_text}\n\n"
                            f"CURRENT QUESTION: {resolved_query}\n\n"
                            f"Answer based strictly on the document context above. "
                            f"Use conversation history only to understand what the user is referring to."
                        ),
                    },
                ],
                max_tokens=config["max_tokens"],
                temperature=0.3,
            )
            answer_text = resp.choices[0].message.content.strip()
            return answer_text + caveat

        except Exception as e:
            return f"An error occurred while generating the answer: {e}"
