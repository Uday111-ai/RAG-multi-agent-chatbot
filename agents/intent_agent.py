"""
INTENT AGENT
------------
Classifies every user query into one of 7 intents BEFORE we do anything else.

Intents:
  summarize    → user wants full document summary  (map-reduce path)
  explain      → user wants detailed explanation of a concept/section
  figure_table → user asking about Fig X, Table X, formula, equation
  factual      → user wants a specific fact, number, date, name
  table        → user wants a GENERATED markdown table from document data
  diagram      → user wants a GENERATED flowchart/diagram from document content
  general      → anything else
"""

import re


class IntentAgent:
    def __init__(self, groq_client):
        self.groq = groq_client

        # ----- Keyword maps (fast path) ----- #
        self._summarize_kw = re.compile(
            r"\b(summar(ize|ise|y)|overview|brief|gist|outline|synopsis|"
            r"what is this (doc|paper|article|book|file) about|"
            r"tell me about (this|the) (doc|paper|article|book|file)|"
            r"what does (this|the) (doc|paper|article|book|file) (say|talk|cover))\b",
            re.IGNORECASE,
        )
        self._diagram_kw = re.compile(
            r"\b(flow\s*(chart|diagram)|draw|sketch|visuali[sz]e|"
            r"mind\s*map|process\s*(flow|diagram)|workflow|"
            r"generate\s*(a\s*)?(diagram|chart|flow)|"
            r"show\s*(me\s*)?(a\s*)?(diagram|flow|chart|map)|"
            r"create\s*(a\s*)?(diagram|flowchart|flow chart))\b",
            re.IGNORECASE,
        )
        self._table_kw = re.compile(
            r"\b(make\s*(a\s*)?table|create\s*(a\s*)?table|generate\s*(a\s*)?table|"
            r"show\s*(me\s*)?(a\s*|in\s*)?table|"
            r"tabulate|put\s*(it\s*)?in\s*(a\s*)?table|"
            r"table\s*(of|for|showing|with)|comparison\s*table|"
            r"list\s*(it\s*)?in\s*(a\s*)?table)\b",
            re.IGNORECASE,
        )
        self._figure_kw = re.compile(
            r"\b(fig(ure)?\.?\s*\d+|table\s*\d+|"
            r"eq(uation)?\.?\s*\d*|formula|illustration|image\s*\d*)\b",
            re.IGNORECASE,
        )
        self._factual_kw = re.compile(
            r"\b(what is the (value|number|amount|result|name|date|year)|"
            r"how many|when (was|is|did)|who (is|was|wrote|created)|"
            r"where (is|was)|which (year|month|day|version|model))\b",
            re.IGNORECASE,
        )
        self._explain_kw = re.compile(
            r"\b(explain|describe|elaborate|tell me (more )?(about|how)|"
            r"what (is|are|does|do)|how (does|do|is)|why (is|does|did)|"
            r"definition of|meaning of|concept of)\b",
            re.IGNORECASE,
        )

    # ------------------------------------------------------------------ #
    def detect(self, query: str) -> str:
        """Return one of: summarize | explain | figure_table | factual | table | diagram | general"""

        # Order matters — check most specific first
        if self._summarize_kw.search(query):
            return "summarize"
        if self._diagram_kw.search(query):
            return "diagram"
        if self._table_kw.search(query):
            return "table"
        if self._figure_kw.search(query):
            return "figure_table"
        if self._factual_kw.search(query):
            return "factual"
        if self._explain_kw.search(query):
            return "explain"

        # LLM fallback for ambiguous queries
        try:
            resp = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Classify the user query into EXACTLY one word from this list:\n"
                            "summarize, explain, figure_table, factual, table, diagram, general\n\n"
                            "summarize   = user wants a summary of the whole document\n"
                            "explain     = user wants a detailed explanation of a topic\n"
                            "figure_table= user asking about a specific figure, table number, formula in doc\n"
                            "factual     = user wants a specific fact, number, name, date\n"
                            "table       = user wants a NEW generated comparison/data table\n"
                            "diagram     = user wants a flowchart, mind map, or process diagram generated\n"
                            "general     = anything else\n\n"
                            "Reply with ONLY the one word. No punctuation. Nothing else."
                        ),
                    },
                    {"role": "user", "content": query},
                ],
                max_tokens=5,
                temperature=0,
            )
            intent = resp.choices[0].message.content.strip().lower()
            valid = {"summarize", "explain", "figure_table", "factual", "table", "diagram", "general"}
            return intent if intent in valid else "general"
        except Exception:
            return "general"
