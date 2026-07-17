"""
ApplyTrack AI — Streamlit chat UI for the tracker agent.

Structure:
    1. Page config + theme (CSS)
    2. Thread-aware stdout capture      <- makes the "live agent log" safe for many concurrent users
    3. Sidebar (branding)
    4. Session state
    5. Chat rendering
    6. Agent execution + live status
    7. Chat input handling
"""

import sys
import time
import queue
import asyncio
import textwrap
import threading
from concurrent.futures import ThreadPoolExecutor

import streamlit as st
from src.agent.tracker import tracker_agent

# ==================================================================
# 1. Page config
# ==================================================================
st.set_page_config(
    page_title="ApplyTrack AI",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.html(
    textwrap.dedent(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
        :root {
            --ink: #0A0D16;
            --ink-2: #12172A;
            --cyan: #22D3EE;
            --violet: #8B5CF6;
            --amber: #F59E0B;
            --text: #E7EAF3;
            --muted: #7C87A6;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 8%, rgba(139,92,246,0.16), transparent 42%),
                radial-gradient(circle at 85% 15%, rgba(34,211,238,0.14), transparent 45%),
                radial-gradient(circle at 50% 100%, rgba(245,158,11,0.07), transparent 50%),
                var(--ink);
            font-family: 'Inter', sans-serif;
        }

        #MainMenu, header, footer {visibility: hidden;}

        /* ---------- Sidebar branding ---------- */
        section[data-testid="stSidebar"] {
            background: var(--ink-2);
            border-right: 1px solid rgba(255,255,255,0.06);
        }
        .brand {
            padding: 0.4rem 0 1.2rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 1rem;
        }
        .brand .logo-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .brand .logo-row span.icon { font-size: 1.4rem; }
        .brand h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            margin: 0;
            background: linear-gradient(100deg, var(--cyan), var(--violet) 45%, var(--amber) 85%);
            background-size: 220% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: sheen 7s ease-in-out infinite;
        }
        .brand p {
            color: var(--muted);
            font-size: 0.78rem;
            margin: 0.3rem 0 0 0;
        }
        @keyframes sheen {
            0%   { background-position: 0% 50%; }
            50%  { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* ---------- Chat bubbles ---------- */
        [data-testid="stChatMessage"] {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 0.55rem 0.3rem;
            animation: rise 0.35s ease both;
        }
        @keyframes rise {
            from { opacity: 0; transform: translateY(10px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ---------- Chat input ---------- */
        .stChatInput {
            padding-top: 0.4rem;
        }
        .stChatInput textarea {
            border-radius: 16px !important;
            border: 1px solid rgba(139,92,246,0.30) !important;
            background: rgba(255,255,255,0.035) !important;
            padding: 0.85rem 1rem !important;
            font-size: 0.95rem !important;
            color: var(--text) !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.18) !important;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }
        .stChatInput textarea::placeholder {
            color: var(--muted) !important;
        }
        .stChatInput textarea:focus {
            border-color: var(--cyan) !important;
            box-shadow: 0 0 0 3px rgba(34,211,238,0.15) !important;
        }

        /* ---------- Buttons (clear + suggestion chips) ---------- */
        .stButton > button {
            border-radius: 999px !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            background: rgba(255,255,255,0.04) !important;
            color: var(--text) !important;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem !important;
            padding: 0.35rem 0.9rem !important;
            transition: all 0.15s ease;
        }
        .stButton > button:hover {
            border-color: var(--cyan) !important;
            color: var(--cyan) !important;
            transform: translateY(-1px);
        }

        /* ---------- Live agent status (real stdout, not a canned loop) ---------- */
        .radar-wrap {
            display: flex;
            align-items: flex-start;
            gap: 0.9rem;
            padding: 0.7rem 1rem;
            background: rgba(139,92,246,0.06);
            border: 1px solid rgba(139,92,246,0.25);
            border-radius: 14px;
            margin-top: 0.3rem;
        }
        .radar {
            position: relative;
            width: 34px;
            height: 34px;
            flex-shrink: 0;
            margin-top: 2px;
        }
        .radar .core {
            position: absolute;
            top: 50%; left: 50%;
            width: 8px; height: 8px;
            margin: -4px 0 0 -4px;
            border-radius: 50%;
            background: var(--violet);
            box-shadow: 0 0 8px var(--violet);
        }
        .radar .ring {
            position: absolute;
            top: 50%; left: 50%;
            width: 8px; height: 8px;
            margin: -4px 0 0 -4px;
            border-radius: 50%;
            border: 1.5px solid var(--violet);
            opacity: 0;
            animation: pulse 1.8s ease-out infinite;
        }
        .radar .ring:nth-child(2) { animation-delay: 0.6s; }
        .radar .ring:nth-child(3) { animation-delay: 1.2s; }
        @keyframes pulse {
            0%   { width: 8px; height: 8px; margin: -4px 0 0 -4px; opacity: 0.8; }
            100% { width: 34px; height: 34px; margin: -17px 0 0 -17px; opacity: 0; }
        }
        .radar-log-block {
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
        }
        .radar-log-dim {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.76rem;
            color: var(--muted);
            opacity: 0.6;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .radar-log {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            color: var(--cyan);
            white-space: pre-wrap;
            word-break: break-word;
        }
        .radar-log .cursor {
            display: inline-block;
            width: 6px; height: 1em;
            background: var(--cyan);
            margin-left: 2px;
            vertical-align: text-bottom;
            animation: blink 0.9s step-end infinite;
        }
        @keyframes blink { 50% { opacity: 0; } }

        /* ---------- Empty state ---------- */
        .empty-hint {
            text-align: center;
            color: var(--muted);
            font-size: 0.88rem;
            padding: 1.2rem 0 0.4rem 0;
        }
        </style>
        """
    )
)

# ==================================================================
# 2. Thread-aware stdout capture
#
# Streamlit runs every user's session in the same process (different
# threads). We can't just do `sys.stdout = some_queue` — that would
# leak one user's agent logs into every other user's browser.
#
# Instead we install ONE proxy, once, for the whole process. It looks
# up the CURRENT thread's id in a registry to find where that
# specific agent run's output should go. Any print() from code that
# isn't a tracked agent run (or that spawns its own thread) just
# falls through to the real terminal, unchanged.
# ==================================================================
_real_stdout = sys.stdout
_log_registry: dict[int, "queue.Queue[str]"] = {}
_registry_lock = threading.Lock()


class _ThreadAwareStdout:
    def write(self, text: str) -> int:
        q = None
        with _registry_lock:
            q = _log_registry.get(threading.get_ident())
        if q is not None:
            if text.strip():
                q.put(text)
        else:
            _real_stdout.write(text)
        return len(text)

    def flush(self) -> None:
        _real_stdout.flush()


if not isinstance(sys.stdout, _ThreadAwareStdout):
    sys.stdout = _ThreadAwareStdout()


def run_agent_with_live_log(prompt: str, log_queue: "queue.Queue[str]") -> str:
    """Runs the agent on this thread, capturing its own prints into log_queue.

    Registered/unregistered by thread id, so concurrent users never see
    each other's logs, even though sys.stdout is shared process-wide.
    """
    tid = threading.get_ident()
    with _registry_lock:
        _log_registry[tid] = log_queue
    try:
        return asyncio.run(tracker_agent(prompt))
    finally:
        with _registry_lock:
            _log_registry.pop(tid, None)


# ==================================================================
# 3. Sidebar — branding lives here now, main screen stays task-only
# ==================================================================
with st.sidebar:
    st.markdown(
        textwrap.dedent(
            """
            <div class="brand">
                <div class="logo-row">
                    <span class="icon">🎯</span>
                    <h1>ApplyTrack AI</h1>
                </div>
                <p>Mission control for your job hunt.</p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==================================================================
# 4. Session state (per-browser-session, isolated by Streamlit already)
# ==================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ==================================================================
# 5. Chat history + empty state
# ==================================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🎯"):
        st.markdown(msg["content"])

if not st.session_state.messages:
    st.markdown(
        '<div class="empty-hint">try one of these, or type your own below ↓</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    chips = [
        (c1, "📋 Show Applications", "Show me all my applications"),
        (c2, "📬 Check Gmail", "Check Gmail for any new application updates"),
    ]
    for col, label, prompt_text in chips:
        with col:
            if st.button(label, use_container_width=True, key=f"chip_{label}"):
                st.session_state.pending_prompt = prompt_text

# ==================================================================
# 6. Agent execution with a live status log fed by real stdout
# ==================================================================
MAX_VISIBLE_LOG_LINES = 4


def render_agent_status(placeholder, log_lines: list[str]) -> None:
    if not log_lines:
        current, history = "starting up", []
    else:
        current, history = log_lines[-1], log_lines[-MAX_VISIBLE_LOG_LINES:-1]

    history_html = "".join(f'<div class="radar-log-dim">{line}</div>' for line in history)
    placeholder.markdown(
        textwrap.dedent(
            f"""
            <div class="radar-wrap">
                <div class="radar">
                    <div class="ring"></div><div class="ring"></div><div class="ring"></div>
                    <div class="core"></div>
                </div>
                <div class="radar-log-block">
                    {history_html}
                    <div class="radar-log">{current}<span class="cursor"></span></div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def get_response(prompt: str) -> str:
    log_queue: "queue.Queue[str]" = queue.Queue()
    log_lines: list[str] = []
    placeholder = st.empty()

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(run_agent_with_live_log, prompt, log_queue)

        while not future.done():
            try:
                line = log_queue.get(timeout=0.1)
                log_lines.append(line.strip())
            except queue.Empty:
                pass
            render_agent_status(placeholder, log_lines)

        # drain anything printed right before the future finished
        while not log_queue.empty():
            log_lines.append(log_queue.get().strip())

        placeholder.empty()
        return future.result()


# ==================================================================
# 7. Chat input
# ==================================================================
typed_prompt = st.chat_input("Ask ApplyTrack AI to manage your applications...")
prompt = typed_prompt or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎯"):
        try:
            response = get_response(prompt)
        except Exception as e:
            response = f"⚠️ Something went wrong: `{e}`"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()