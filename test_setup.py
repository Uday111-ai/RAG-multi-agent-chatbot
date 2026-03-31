"""
test_setup.py
Run this ONCE before starting the app to verify everything is working.
"""

print("\n🔍 Running setup verification...\n")

# Test 1 — .env / API Key
try:
    from dotenv import load_dotenv
    import os
    load_dotenv()
    key = os.getenv("GROQ_API_KEY")
    if key and key != "your_groq_api_key_here":
        print("✅ GROQ_API_KEY loaded from .env")
    else:
        print("❌ GROQ_API_KEY missing or not set. Open .env and paste your key.")
        exit(1)
except Exception as e:
    print(f"❌ python-dotenv error: {e}")
    exit(1)

# Test 2 — PyMuPDF
try:
    import fitz
    print("✅ PyMuPDF (fitz) — OK")
except Exception as e:
    print(f"❌ PyMuPDF: {e}")

# Test 3 — Sentence Transformers (embedding model)
try:
    from sentence_transformers import SentenceTransformer
    print("⏳ Loading embedding model (first time = downloads ~90MB, then cached)...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    vec = model.encode(["hello world"])
    print(f"✅ Embedding model — OK (vector size: {vec.shape[1]})")
except Exception as e:
    print(f"❌ sentence-transformers: {e}")

# Test 4 — ChromaDB
try:
    import chromadb
    client = chromadb.PersistentClient(path="./chroma_db")
    print("✅ ChromaDB — OK")
except Exception as e:
    print(f"❌ ChromaDB: {e}")

# Test 5 — Groq API
try:
    from groq import Groq
    client = Groq(api_key=key)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Reply with just the word: READY"}],
        max_tokens=5,
    )
    reply = resp.choices[0].message.content.strip()
    print(f"✅ Groq API (LLaMA 3.3 70B) — OK  [model replied: {reply}]")
except Exception as e:
    print(f"❌ Groq API: {e}")

# Test 6 — Streamlit
try:
    import streamlit
    print(f"✅ Streamlit {streamlit.__version__} — OK")
except Exception as e:
    print(f"❌ Streamlit: {e}")

print("\n🎉 All checks done. If all are ✅, run:  streamlit run app.py\n")
