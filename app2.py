"""
app.py - DocMind AI
No sidebar - uses 2-column layout so nothing ever gets hidden.
Run with: python -m streamlit run app.py
"""

import streamlit as st
import os, tempfile, time, json

CHAT_HISTORY_FILE = "chat_history.json"

def save_chat_history(history):
    try:
        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_chat_history():
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

st.set_page_config(
    page_title="DocMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #0b0d12; color: #dde1ed; }
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
.left-panel { background: #10121a; border: 1px solid #1d2030; border-radius: 14px; padding: 1.2rem; min-height: 90vh; }
.main-title { font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800; color:#fff; margin:0; }
.main-subtitle { font-size:2.2rem; color:#6b7280; margin-top:3px; margin-bottom:1rem; }
.user-bubble { background:#161825; border:1px solid #252840; border-left:3px solid #7c6ff7; border-radius:10px; padding:0.9rem 1.1rem; margin:0.6rem 0; font-size:0.95rem; }
.ai-bubble { background:#10121a; border:1px solid #1d2030; border-left:3px solid #10b981; border-radius:10px; padding:0.9rem 1.1rem; margin:0.6rem 0; font-size:0.95rem; line-height:1.75; }
.bubble-label { font-size:0.68rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:5px; }
.user-label { color:#7c6ff7; }
.ai-label   { color:#10b981; }
.intent-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.65rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px; }
.badge-summarize    { background:#1e293b; color:#38bdf8; border:1px solid #0284c7; }
.badge-explain      { background:#1a1f2e; color:#a78bfa; border:1px solid #7c3aed; }
.badge-figure_table { background:#1f2d1f; color:#34d399; border:1px solid #059669; }
.badge-factual      { background:#2d1f1f; color:#fb923c; border:1px solid #c2410c; }
.badge-general      { background:#1e1e2e; color:#94a3b8; border:1px solid #475569; }
.badge-table        { background:#1e2d1e; color:#4ade80; border:1px solid #16a34a; }
.badge-diagram      { background:#1e1e2d; color:#818cf8; border:1px solid #4f46e5; }
.doc-card { background:#161825; border:1px solid #252840; border-radius:10px; padding:0.8rem 1rem; margin:0.5rem 0 1rem 0; }
.doc-card-title { font-family:'Syne',sans-serif; font-weight:700; font-size:0.82rem; color:#fff; margin-bottom:4px; word-break:break-word; }
.doc-stat { font-size:0.73rem; color:#6b7280; }
.dot { color:#10b981; margin-right:4px; }
.divider { border:none; border-top:1px solid #1d2030; margin:0.8rem 0; }
.section-label { font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:#4b5563; margin-bottom:6px; margin-top:0.8rem; }
.welcome-box { background:#161825; border:1px dashed #252840; border-radius:12px; padding:2.5rem 2rem; text-align:center; color:#6b7280; margin-top:3rem; }
.welcome-icon { font-size:2.5rem; margin-bottom:0.5rem; }
.welcome-title { font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:#9ca3af; margin-bottom:0.4rem; }
.stButton > button { background:#1d1f30 !important; color:#dde1ed !important; border:1px solid #252840 !important; border-radius:8px !important; font-size:0.8rem !important; padding:0.35rem 0.8rem !important; width:100% !important; text-align:left !important; }
.stButton > button:hover { background:#252840 !important; border-color:#7c6ff7 !important; color:#fff !important; }
.stTextInput > div > div > input { background:#161825 !important; border:1px solid #252840 !important; border-radius:8px !important; color:#dde1ed !important; font-size:0.95rem !important; padding:0.6rem 0.8rem !important; }
.stTextInput > div > div > input:focus { border-color:#7c6ff7 !important; box-shadow:0 0 0 2px rgba(124,111,247,0.15) !important; }
.stFormSubmitButton > button { background:#7c6ff7 !important; color:#fff !important; border:none !important; border-radius:8px !important; font-weight:500 !important; padding:0.45rem 1.5rem !important; width:auto !important; }
.stFormSubmitButton > button:hover { background:#6358d4 !important; }
[data-testid="stFileUploader"] { background:#161825; border:1px dashed #252840; border-radius:10px; }
[data-testid="stFileUploader"] * { color:#9ca3af !important; }
#MainMenu { visibility:hidden; }
footer    { visibility:hidden; }
header    { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


def init_session():
    defaults = {
        "orchestrator": None,
        "chat_history": load_chat_history(),
        "doc_loaded": False,
        "doc_info": {},
        "input_counter": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

@st.cache_resource(show_spinner=False)
def get_orchestrator():
    from orchestrator import Orchestrator
    return Orchestrator()


left_col, right_col = st.columns([1, 2.8], gap="medium")


with left_col:
    # st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<p class="main-title">🧠 DocMind</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Multi-Agent Document Intelligence</p>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown('<p class="section-label">📂 Upload Document</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file is not None:
        if st.button("⚡ Process Document"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            status_ph = st.empty()
            def update_status(msg): status_ph.info(msg)
            try:
                with st.spinner("Loading agents..."):
                    orch = get_orchestrator()
                update_status("📄 Starting ingestion...")
                meta = orch.load_document(tmp_path, progress_callback=update_status)
                st.session_state.orchestrator = orch
                st.session_state.doc_loaded   = True
                st.session_state.doc_info     = meta
                st.session_state.chat_history = []
                save_chat_history([])
                status_ph.success("✅ Document ready!")
                time.sleep(1)
                status_ph.empty()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                try: os.unlink(tmp_path)
                except: pass

    if st.session_state.doc_loaded and st.session_state.doc_info:
        info = st.session_state.doc_info
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">📑 Loaded Document</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="doc-card">
            <div class="doc-card-title">📄 {info.get('doc_name','Document')}</div>
            <div class="doc-stat"><span class="dot">●</span>{info.get('num_pages','?')} pages</div>
            <div class="doc-stat"><span class="dot">●</span>{info.get('num_chunks','?')} chunks indexed</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">💡 Example Queries</p>', unsafe_allow_html=True)
    for ex in ["Summarize this document","Explain the methodology","What does Figure 1 show?",
               "What are the main conclusions?","Explain the formula in section 3","What is the dataset used?"]:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state["prefill_query"] = ex
            st.rerun()

    if st.session_state.chat_history:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            save_chat_history([])
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


with right_col:
    if not st.session_state.doc_loaded:
        st.markdown("""
        <div class="welcome-box">
            <div class="welcome-icon">🧠</div>
            <div class="welcome-title">Upload a document to get started</div>
            <div>Supports PDF files — research papers, textbooks, reports, manuals</div>
            <br>
            <div style="font-size:0.8rem;color:#4b5563;">
                Ask anything: summarize • explain concepts • figures &amp; tables • formulas • Q&amp;A
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        if not st.session_state.chat_history:
            info = st.session_state.doc_info
            st.markdown(f"""
            <div class="welcome-box">
                <div class="welcome-icon">✅</div>
                <div class="welcome-title">"{info.get('doc_name','Document')}" is ready</div>
                <div>{info.get('num_pages','?')} pages · {info.get('num_chunks','?')} chunks indexed</div>
                <br>
                <div style="font-size:0.8rem;color:#4b5563;">Ask me anything about this document ↓</div>
            </div>""", unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="user-bubble">
                    <div class="bubble-label user-label">You</div>
                    {msg["content"]}
                </div>""", unsafe_allow_html=True)
            else:
                intent = msg.get("intent", "general")
                content = msg["content"]
                intent_label = intent.replace('_',' ').title()

                # Check if content has a mermaid code block
                import re as _re
                mermaid_match = _re.search(r"```mermaid\s*([\s\S]*?)```", content)
                has_mermaid = mermaid_match is not None

                # Render the AI bubble header
                st.markdown(f"""
                <div class="ai-bubble">
                    <div class="bubble-label ai-label">DocMind</div>
                    <span class="intent-badge badge-{intent}">{intent_label}</span>
                    <div style="white-space:pre-wrap;">{content if not has_mermaid else content[:mermaid_match.start()].strip()}</div>
                </div>""", unsafe_allow_html=True)

                # Render Mermaid diagram if present
                if has_mermaid:
                    mermaid_code = mermaid_match.group(1).strip()
                    st.markdown(f"""
                    <div style="background:#0f1117;border:1px solid #1d2030;border-radius:10px;padding:1rem;margin:0.5rem 0;">
                        <div class="mermaid">{mermaid_code}</div>
                    </div>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>mermaid.initialize({{startOnLoad:true, theme:'dark'}});</script>
                    """, unsafe_allow_html=True)
                    # Also show anything after the mermaid block
                    after = content[mermaid_match.end():].strip()
                    if after:
                        st.markdown(f'<div class="ai-bubble" style="margin-top:0.2rem;"><div style="white-space:pre-wrap;">{after}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        prefill = st.session_state.pop("prefill_query", "")

        with st.form(key=f"qform_{st.session_state.input_counter}", clear_on_submit=True):
            user_input = st.text_input(
                "query", value=prefill,
                placeholder="Ask anything about the document — press Enter or click Send",
                label_visibility="collapsed",
            )
            send = st.form_submit_button("Send ➤")

        if send and user_input.strip():
            query = user_input.strip()
            orch  = st.session_state.orchestrator
            st.session_state.input_counter += 1
            st.session_state.chat_history.append({"role":"user","content":query})

            progress_ph = st.empty()
            def show_progress(msg): progress_ph.info(msg)

            with st.spinner("Thinking..."):
                try:
                    result = orch.query(query, progress_callback=show_progress)
                    answer, intent = result["answer"], result["intent"]
                except Exception as e:
                    answer, intent = f"An error occurred: {e}", "general"

            progress_ph.empty()
            st.session_state.chat_history.append({"role":"assistant","content":answer,"intent":intent})
            save_chat_history(st.session_state.chat_history)
            st.rerun()
