"""
app.py - DocMind AI
Premium dark UI with glassmorphism, animated gradients, and micro-interactions.
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

# ─────────────────────────────────────────────────────────────
#  PREMIUM CSS DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

/* ── Reset & Base ────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ── App Background ──────────────────────────────── */
.stApp {
    background: #050a12;
    color: #d0d8e8;
    overflow-x: hidden;
}

/* ── Animated Floating Orbs ──────────────────────── */
.bg-orbs {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.bg-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.5;
    will-change: transform;
}
.bg-orb-1 {
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(14,165,233,0.18) 0%, transparent 70%);
    top: -10%; left: -5%;
    animation: orbFloat1 18s ease-in-out infinite alternate;
}
.bg-orb-2 {
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(245,158,11,0.14) 0%, transparent 70%);
    bottom: -8%; right: -5%;
    animation: orbFloat2 22s ease-in-out infinite alternate;
}
.bg-orb-3 {
    width: 350px; height: 350px;
    background: radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%);
    top: 40%; left: 50%;
    animation: orbFloat3 25s ease-in-out infinite alternate;
}
.bg-orb-4 {
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%);
    top: 10%; right: 20%;
    animation: orbFloat4 20s ease-in-out infinite alternate;
}
.bg-orb-5 {
    width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(56,189,248,0.1) 0%, transparent 70%);
    bottom: 20%; left: 30%;
    animation: orbFloat5 16s ease-in-out infinite alternate;
}

@keyframes orbFloat1 {
    0%   { transform: translate(0, 0) scale(1); }
    50%  { transform: translate(80px, 60px) scale(1.15); }
    100% { transform: translate(-40px, 120px) scale(0.95); }
}
@keyframes orbFloat2 {
    0%   { transform: translate(0, 0) scale(1); }
    50%  { transform: translate(-70px, -50px) scale(1.1); }
    100% { transform: translate(50px, -100px) scale(1.05); }
}
@keyframes orbFloat3 {
    0%   { transform: translate(0, 0) scale(1); }
    50%  { transform: translate(-100px, 40px) scale(0.9); }
    100% { transform: translate(60px, -60px) scale(1.1); }
}
@keyframes orbFloat4 {
    0%   { transform: translate(0, 0) scale(1); }
    50%  { transform: translate(50px, 80px) scale(1.2); }
    100% { transform: translate(-80px, 30px) scale(0.9); }
}
@keyframes orbFloat5 {
    0%   { transform: translate(0, 0) scale(1); }
    50%  { transform: translate(70px, -70px) scale(1.15); }
    100% { transform: translate(-50px, 50px) scale(1); }
}

/* ── Animated Grid Overlay ───────────────────────── */
.bg-grid {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    background-image:
        linear-gradient(rgba(14,165,233,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(14,165,233,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridScroll 30s linear infinite;
}
@keyframes gridScroll {
    0%   { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}

/* ── Scanning Light Line ─────────────────────────── */
.bg-scanline {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.bg-scanline::after {
    content: '';
    position: absolute;
    left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, rgba(14,165,233,0.15) 30%, rgba(245,158,11,0.1) 70%, transparent 100%);
    box-shadow: 0 0 20px rgba(14,165,233,0.1);
    animation: scanMove 8s ease-in-out infinite;
}
@keyframes scanMove {
    0%   { top: -2px; opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { top: 100vh; opacity: 0; }
}

/* ── Hide Streamlit defaults ─────────────────────── */
[data-testid="stSidebar"]        { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
#MainMenu, footer, header        { visibility: hidden; }

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
    position: relative;
    z-index: 1;
}

/* ── Scrollbar ───────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(14,165,233,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(14,165,233,0.5); }

/* ── Left Panel ──────────────────────────────────── */
.left-panel-glass {
    background: rgba(8,14,28,0.75);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(14,165,233,0.12);
    border-radius: 20px;
    padding: 1.6rem 1.3rem;
    min-height: 88vh;
    position: relative;
    overflow: hidden;
}
.left-panel-glass::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(14,165,233,0.4) 50%, transparent 100%);
}

/* ── Logo / Brand ────────────────────────────────── */
.brand-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
}
.brand-icon {
    width: 48px; height: 48px;
    border-radius: 14px;
    background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 50%, #0ea5e9 100%);
    background-size: 200% 200%;
    animation: gradShift 4s ease-in-out infinite;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    box-shadow: 0 4px 20px rgba(14,165,233,0.35);
}
@keyframes gradShift {
    0%,100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
.brand-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.3px;
}
.brand-tagline {
    font-size: 0.82rem;
    color: rgba(148,163,184,0.6);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 500;
    margin-top: -2px;
    margin-bottom: 1.2rem;
}

/* ── Dividers ────────────────────────────────────── */
.glass-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(14,165,233,0.18) 50%, transparent 100%);
    margin: 1rem 0;
}

/* ── Section Labels ──────────────────────────────── */
.section-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(148,163,184,0.55);
    margin-bottom: 8px;
    margin-top: 0.6rem;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── File Uploader ───────────────────────────────── */
[data-testid="stFileUploader"] {
    background: rgba(10,18,35,0.6);
    border: 1px dashed rgba(14,165,233,0.2);
    border-radius: 14px;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(14,165,233,0.45);
    box-shadow: 0 0 20px rgba(14,165,233,0.08);
}
[data-testid="stFileUploader"] * { color: #64748b !important; }

/* ── Document Card ───────────────────────────────── */
.doc-card-glass {
    background: rgba(14,165,233,0.06);
    border: 1px solid rgba(14,165,233,0.15);
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    margin: 0.4rem 0 0.8rem 0;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}
.doc-card-glass:hover {
    border-color: rgba(14,165,233,0.3);
    box-shadow: 0 4px 24px rgba(14,165,233,0.1);
}
.doc-card-glass::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 60px; height: 60px;
    background: radial-gradient(circle, rgba(14,165,233,0.15) 0%, transparent 70%);
    border-radius: 0 14px 0 50%;
}
.doc-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    color: #e2e8f0;
    margin-bottom: 8px;
    word-break: break-word;
    display: flex;
    align-items: center;
    gap: 8px;
}
.doc-stats {
    display: flex;
    gap: 16px;
}
.doc-stat-item {
    font-size: 0.85rem;
    color: rgba(148,163,184,0.7);
    display: flex;
    align-items: center;
    gap: 5px;
}
.stat-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #f59e0b;
    box-shadow: 0 0 8px rgba(245,158,11,0.5);
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(0.85); }
}

/* ── Example Query Pills ─────────────────────────── */
.stButton > button {
    background: rgba(10,18,35,0.6) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(14,165,233,0.12) !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
    padding: 0.5rem 1rem !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.25s ease !important;
    font-weight: 400 !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: rgba(14,165,233,0.1) !important;
    border-color: rgba(14,165,233,0.35) !important;
    color: #7dd3fc !important;
    transform: translateX(4px) !important;
    box-shadow: 0 2px 12px rgba(14,165,233,0.1) !important;
}

/* ── Chat Bubbles ────────────────────────────────── */
.user-bubble {
    background: rgba(14,165,233,0.05);
    border: 1px solid rgba(14,165,233,0.12);
    border-left: 3px solid #0ea5e9;
    border-radius: 4px 14px 14px 14px;
    padding: 1.1rem 1.3rem;
    margin: 0.7rem 0;
    font-size: 1.05rem;
    animation: fadeSlideIn 0.35s ease-out;
    line-height: 1.7;
}
.ai-bubble {
    background: rgba(245,158,11,0.04);
    border: 1px solid rgba(245,158,11,0.1);
    border-left: 3px solid #f59e0b;
    border-radius: 14px 4px 14px 14px;
    padding: 1.1rem 1.3rem;
    margin: 0.7rem 0;
    font-size: 1.05rem;
    line-height: 1.8;
    animation: fadeSlideIn 0.35s ease-out;
}
@keyframes fadeSlideIn {
    0% { opacity: 0; transform: translateY(12px); }
    100% { opacity: 1; transform: translateY(0); }
}

.bubble-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.user-label { color: #38bdf8; }
.ai-label   { color: #fbbf24; }
.user-avatar, .ai-avatar {
    width: 20px; height: 20px;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6rem;
}
.user-avatar { background: rgba(14,165,233,0.2); }
.ai-avatar   { background: rgba(245,158,11,0.2); }

/* ── Intent Badges ───────────────────────────────── */
.intent-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
}
.badge-summarize    { background: rgba(56,189,248,0.1); color: #38bdf8; border: 1px solid rgba(56,189,248,0.25); }
.badge-explain      { background: rgba(245,158,11,0.1); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }
.badge-figure_table { background: rgba(52,211,153,0.1); color: #34d399; border: 1px solid rgba(52,211,153,0.25); }
.badge-factual      { background: rgba(251,146,60,0.1);  color: #fb923c; border: 1px solid rgba(251,146,60,0.25); }
.badge-general      { background: rgba(148,163,184,0.08); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2); }
.badge-table        { background: rgba(74,222,128,0.1);  color: #4ade80; border: 1px solid rgba(74,222,128,0.25); }
.badge-diagram      { background: rgba(129,140,248,0.1); color: #818cf8; border: 1px solid rgba(129,140,248,0.25); }

/* ── Welcome Hero ────────────────────────────────── */
.welcome-hero {
    text-align: center;
    padding: 4rem 2rem;
    margin-top: 2rem;
}
.welcome-hero-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    animation: breathe 3s ease-in-out infinite;
}
@keyframes breathe {
    0%,100% { transform: scale(1); filter: drop-shadow(0 0 8px rgba(14,165,233,0.3)); }
    50% { transform: scale(1.08); filter: drop-shadow(0 0 20px rgba(14,165,233,0.5)); }
}
.welcome-hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #e2e8f0 0%, #38bdf8 50%, #fbbf24 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.6rem;
}
.welcome-hero-sub {
    font-size: 1.3rem;
    color: rgba(148,163,184,0.6);
    max-width: 440px;
    margin: 0 auto 1.5rem auto;
    line-height: 1.6;
}
.welcome-features {
    display: flex;
    justify-content: center;
    gap: 24px;
    flex-wrap: wrap;
    margin-top: 1.5rem;
}
.welcome-feature {
    background: rgba(10,18,35,0.5);
    border: 1px solid rgba(14,165,233,0.1);
    border-radius: 12px;
    padding: 14px 20px;
    font-size: 1.1rem;
    color: rgba(148,163,184,0.7);
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.25s ease;
}
.welcome-feature:hover {
    border-color: rgba(14,165,233,0.3);
    color: #7dd3fc;
}

/* ── Ready State ─────────────────────────────────── */
.ready-hero {
    text-align: center;
    padding: 3rem 2rem;
    margin-top: 2rem;
    background: rgba(14,165,233,0.03);
    border: 1px solid rgba(14,165,233,0.1);
    border-radius: 20px;
}
.ready-icon {
    font-size: 3rem;
    margin-bottom: 0.8rem;
}
.ready-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.4rem;
}
.ready-sub {
    font-size: 0.98rem;
    color: rgba(148,163,184,0.6);
}
.ready-stats {
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 1rem;
}
.ready-stat {
    background: rgba(14,165,233,0.07);
    border: 1px solid rgba(14,165,233,0.15);
    border-radius: 10px;
    padding: 10px 18px;
    font-size: 0.9rem;
    color: #38bdf8;
}

/* ── Input Area ──────────────────────────────────── */
.stTextInput > div > div > input {
    background: rgba(8,14,28,0.8) !important;
    border: 1px solid rgba(14,165,233,0.15) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-size: 1.05rem !important;
    padding: 0.75rem 1.1rem !important;
    transition: all 0.25s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(14,165,233,0.45) !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.1), 0 4px 20px rgba(14,165,233,0.08) !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(148,163,184,0.4) !important;
}

.stFormSubmitButton > button {
    background: linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
    width: auto !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 16px rgba(14,165,233,0.3) !important;
    transition: all 0.25s ease !important;
}
.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%) !important;
    box-shadow: 0 6px 24px rgba(14,165,233,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Process Button ──────────────────────────────── */
.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #6c5ce7 0%, #7c6ff7 100%) !important;
    color: #fff !important;
    border: none !important;
}

/* ── Rising Bubbles ──────────────────────────────── */
.bg-bubbles {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.bubble {
    position: absolute;
    bottom: -60px;
    border-radius: 50%;
    opacity: 0;
    animation: bubbleRise linear infinite;
}
.bubble::after {
    content: '';
    position: absolute;
    top: 15%; left: 20%;
    width: 30%; height: 20%;
    background: rgba(255,255,255,0.15);
    border-radius: 50%;
    transform: rotate(-30deg);
}

/* Bubble sizes */
.bubble-xs { width: 6px;  height: 6px; }
.bubble-sm { width: 10px; height: 10px; }
.bubble-md { width: 16px; height: 16px; }
.bubble-lg { width: 24px; height: 24px; }
.bubble-xl { width: 34px; height: 34px; }
.bubble-xxl{ width: 42px; height: 42px; }

/* Bubble colors */
.bubble-blue {
    background: radial-gradient(circle at 30% 30%, rgba(56,189,248,0.35), rgba(14,165,233,0.15));
    border: 1px solid rgba(56,189,248,0.2);
    box-shadow: 0 0 8px rgba(14,165,233,0.15), inset 0 0 6px rgba(56,189,248,0.1);
}
.bubble-amber {
    background: radial-gradient(circle at 30% 30%, rgba(251,191,36,0.3), rgba(245,158,11,0.12));
    border: 1px solid rgba(251,191,36,0.18);
    box-shadow: 0 0 8px rgba(245,158,11,0.12), inset 0 0 6px rgba(251,191,36,0.08);
}
.bubble-teal {
    background: radial-gradient(circle at 30% 30%, rgba(52,211,153,0.3), rgba(16,185,129,0.12));
    border: 1px solid rgba(52,211,153,0.18);
    box-shadow: 0 0 8px rgba(16,185,129,0.12), inset 0 0 6px rgba(52,211,153,0.08);
}
.bubble-purple {
    background: radial-gradient(circle at 30% 30%, rgba(167,139,250,0.3), rgba(139,92,246,0.12));
    border: 1px solid rgba(167,139,250,0.18);
    box-shadow: 0 0 8px rgba(139,92,246,0.12), inset 0 0 6px rgba(167,139,250,0.08);
}

@keyframes bubbleRise {
    0%   { transform: translateX(0) scale(0.4); opacity: 0; bottom: -60px; }
    5%   { opacity: 0.7; transform: translateX(0) scale(0.8); }
    15%  { transform: translateX(15px) scale(1); }
    25%  { transform: translateX(-10px) scale(1); }
    35%  { transform: translateX(12px) scale(1); }
    45%  { transform: translateX(-8px) scale(1); opacity: 0.6; }
    55%  { transform: translateX(10px) scale(1); }
    65%  { transform: translateX(-12px) scale(1); }
    75%  { transform: translateX(6px) scale(1); opacity: 0.4; }
    85%  { transform: translateX(-6px) scale(1.05); opacity: 0.25; }
    92%  { transform: translateX(3px) scale(1.15); opacity: 0.15; }
    100% { transform: translateX(0) scale(1.4); opacity: 0; bottom: 105vh; }
}

/* Staggered delays and speeds for each bubble */
.b1  { left: 3%;  animation-duration: 14s; animation-delay: 0s; }
.b2  { left: 8%;  animation-duration: 18s; animation-delay: 2s; }
.b3  { left: 14%; animation-duration: 11s; animation-delay: 4s; }
.b4  { left: 20%; animation-duration: 16s; animation-delay: 1s; }
.b5  { left: 26%; animation-duration: 20s; animation-delay: 3s; }
.b6  { left: 33%; animation-duration: 13s; animation-delay: 6s; }
.b7  { left: 38%; animation-duration: 17s; animation-delay: 0.5s; }
.b8  { left: 44%; animation-duration: 12s; animation-delay: 5s; }
.b9  { left: 50%; animation-duration: 19s; animation-delay: 2.5s; }
.b10 { left: 55%; animation-duration: 15s; animation-delay: 7s; }
.b11 { left: 60%; animation-duration: 11s; animation-delay: 1.5s; }
.b12 { left: 65%; animation-duration: 21s; animation-delay: 4.5s; }
.b13 { left: 70%; animation-duration: 14s; animation-delay: 3.5s; }
.b14 { left: 75%; animation-duration: 16s; animation-delay: 8s; }
.b15 { left: 80%; animation-duration: 12s; animation-delay: 0.8s; }
.b16 { left: 85%; animation-duration: 18s; animation-delay: 6.5s; }
.b17 { left: 90%; animation-duration: 13s; animation-delay: 2.2s; }
.b18 { left: 94%; animation-duration: 22s; animation-delay: 5.5s; }
.b19 { left: 11%; animation-duration: 15s; animation-delay: 9s; }
.b20 { left: 47%; animation-duration: 10s; animation-delay: 7.5s; }

</style>
""", unsafe_allow_html=True)

# ── Animated Background Layers ──
st.markdown("""
<div class="bg-orbs">
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>
    <div class="bg-orb bg-orb-4"></div>
    <div class="bg-orb bg-orb-5"></div>
</div>
<div class="bg-grid"></div>
<div class="bg-scanline"></div>
<div class="bg-bubbles">
    <div class="bubble bubble-sm bubble-blue b1"></div>
    <div class="bubble bubble-lg bubble-amber b2"></div>
    <div class="bubble bubble-xs bubble-teal b3"></div>
    <div class="bubble bubble-xl bubble-blue b4"></div>
    <div class="bubble bubble-md bubble-purple b5"></div>
    <div class="bubble bubble-sm bubble-amber b6"></div>
    <div class="bubble bubble-xxl bubble-blue b7"></div>
    <div class="bubble bubble-xs bubble-teal b8"></div>
    <div class="bubble bubble-lg bubble-purple b9"></div>
    <div class="bubble bubble-md bubble-blue b10"></div>
    <div class="bubble bubble-sm bubble-amber b11"></div>
    <div class="bubble bubble-xl bubble-teal b12"></div>
    <div class="bubble bubble-xs bubble-blue b13"></div>
    <div class="bubble bubble-lg bubble-purple b14"></div>
    <div class="bubble bubble-xxl bubble-amber b15"></div>
    <div class="bubble bubble-md bubble-blue b16"></div>
    <div class="bubble bubble-sm bubble-teal b17"></div>
    <div class="bubble bubble-xs bubble-amber b18"></div>
    <div class="bubble bubble-lg bubble-blue b19"></div>
    <div class="bubble bubble-md bubble-purple b20"></div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────
#  LAYOUT
# ─────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 2.8], gap="medium")


# ═══════════════════════════════════════════════════
#  LEFT PANEL
# ═══════════════════════════════════════════════════
with left_col:
    # ── Brand ──
    st.markdown("""
    <div class="brand-container">
        <div class="brand-icon">🧠</div>
        <div>
            <div class="brand-name">DocMind</div>
        </div>
    </div>
    <div class="brand-tagline">Multi-Agent Document Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="glass-divider">', unsafe_allow_html=True)

    # ── Upload ──
    st.markdown('<div class="section-label">📂 Upload Document</div>', unsafe_allow_html=True)
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

    # ── Document Info Card ──
    if st.session_state.doc_loaded and st.session_state.doc_info:
        info = st.session_state.doc_info
        st.markdown('<hr class="glass-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">📑 Active Document</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="doc-card-glass">
            <div class="doc-name">
                <span>📄</span> {info.get('doc_name','Document')}
            </div>
            <div class="doc-stats">
                <div class="doc-stat-item"><span class="stat-dot"></span>{info.get('num_pages','?')} pages</div>
                <div class="doc-stat-item"><span class="stat-dot"></span>{info.get('num_chunks','?')} chunks</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Example Queries ──
    st.markdown('<hr class="glass-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">💡 Quick Prompts</div>', unsafe_allow_html=True)
    examples = [
        "Summarize this document",
        "Explain the methodology",
        "What does Figure 1 show?",
        "What are the main conclusions?",
        "Explain the formula in section 3",
        "What is the dataset used?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state["prefill_query"] = ex
            st.rerun()

    # ── Actions ──
    if st.session_state.chat_history:
        st.markdown('<hr class="glass-divider">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                save_chat_history([])
                if st.session_state.orchestrator:
                    st.session_state.orchestrator.clear_memory()
                st.rerun()
        with col2:
            if st.button("🧠 Clear Memory"):
                if st.session_state.orchestrator:
                    st.session_state.orchestrator.clear_memory()
                st.success("Memory cleared!", icon="✅")

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#  RIGHT PANEL — Chat Area
# ═══════════════════════════════════════════════════
with right_col:
    # ── Welcome State ──
    if not st.session_state.doc_loaded:
        st.markdown("""
        <div class="welcome-hero">
            <div class="welcome-hero-icon">🧠</div>
            <div class="welcome-hero-title">Upload a document to begin</div>
            <div class="welcome-hero-sub">
                Drop a PDF — research papers, textbooks, reports, or manuals — and ask anything about it.
            </div>
            <div class="welcome-features">
                <div class="welcome-feature">📝 Summarize</div>
                <div class="welcome-feature">🔍 Explain Concepts</div>
                <div class="welcome-feature">📊 Figures & Tables</div>
                <div class="welcome-feature">🧮 Formulas</div>
                <div class="welcome-feature">💬 Q&A</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        # ── Document Ready State ──
        if not st.session_state.chat_history:
            info = st.session_state.doc_info
            st.markdown(f"""
            <div class="ready-hero">
                <div class="ready-icon">✅</div>
                <div class="ready-title">"{info.get('doc_name','Document')}" is ready</div>
                <div class="ready-sub">Your document has been processed and indexed. Ask me anything!</div>
                <div class="ready-stats">
                    <div class="ready-stat">📄 {info.get('num_pages','?')} pages</div>
                    <div class="ready-stat">🧩 {info.get('num_chunks','?')} chunks indexed</div>
                </div>
            </div>""", unsafe_allow_html=True)

        # ── Chat Messages ──
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="user-bubble">
                    <div class="bubble-label user-label">
                        <span class="user-avatar">👤</span> You
                    </div>
                    {msg["content"]}
                </div>""", unsafe_allow_html=True)
            else:
                intent = msg.get("intent", "general")
                content = msg["content"]
                intent_label = intent.replace('_',' ').title()

                # Check for mermaid code block
                import re as _re
                mermaid_match = _re.search(r"```mermaid\s*([\s\S]*?)```", content)
                has_mermaid = mermaid_match is not None

                st.markdown(f"""
                <div class="ai-bubble">
                    <div class="bubble-label ai-label">
                        <span class="ai-avatar">🧠</span> DocMind
                    </div>
                    <span class="intent-badge badge-{intent}">{intent_label}</span>
                    <div style="white-space:pre-wrap;">{content if not has_mermaid else content[:mermaid_match.start()].strip()}</div>
                </div>""", unsafe_allow_html=True)

                # Render Mermaid diagram
                if has_mermaid:
                    mermaid_code = mermaid_match.group(1).strip()
                    st.markdown(f"""
                    <div style="background:rgba(12,15,25,0.8);border:1px solid rgba(108,92,231,0.15);border-radius:14px;padding:1.2rem;margin:0.5rem 0;">
                        <div class="mermaid">{mermaid_code}</div>
                    </div>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>mermaid.initialize({{startOnLoad:true, theme:'dark'}});</script>
                    """, unsafe_allow_html=True)
                    after = content[mermaid_match.end():].strip()
                    if after:
                        st.markdown(f'<div class="ai-bubble" style="margin-top:0.2rem;"><div style="white-space:pre-wrap;">{after}</div></div>', unsafe_allow_html=True)

        # ── Input Form ──
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
