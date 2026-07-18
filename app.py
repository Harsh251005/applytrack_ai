import sys
import html
import time
import queue
import asyncio
import contextvars
import threading
from concurrent.futures import ThreadPoolExecutor

import streamlit as st
from src.agent.tracker import tracker_agent

# ==================================================================
# 1. Page Config & Modern UI Theme
# ==================================================================
st.set_page_config(
    page_title="ApplyTrack AI",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide sidebar entirely and inject stunning modern CSS
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
<style>
    /* Global Variables */
    :root {
        --bg-color: #0d0f19;
        --brand-blue: #0072ff;
        --brand-cyan: #00c6ff;
        --brand-pink: #f857a6;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --text-main: #e2e8f0;
        --text-muted: #94a3b8;
    }

    /* Animated Background */
    .stApp {
        background-color: var(--bg-color);
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(0, 198, 255, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(248, 87, 166, 0.1) 0%, transparent 40%);
        background-attachment: fixed;
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-main);
    }

    /* Hide unnecessary UI */
    [data-testid="collapsedControl"], #MainMenu, footer, header { display: none !important; }

    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 8rem !important; /* Space for input */
        max-width: 800px;
    }

    /* ---------- Animated Logo & Header ---------- */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-bottom: 2.5rem;
        animation: fadeIn 1s ease-out;
        text-align: center;
    }

    .logo-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }

    .target-icon {
        font-size: 2.8rem;
        animation: pulseLogo 2.5s infinite;
        filter: drop-shadow(0 0 10px rgba(0, 198, 255, 0.6));
    }

    .brand-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(to right, var(--brand-cyan), var(--brand-blue), var(--brand-pink), var(--brand-cyan));
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textShine 5s linear infinite;
    }

    .brand-subtitle {
        color: var(--text-muted);
        font-size: 1rem;
        margin-top: 5px;
        font-weight: 400;
    }

    /* ---------- Chat Layout & Bubbles ---------- */
    /* Base Container Rule */
    div[class*="st-key-bubble-"], div[class*="st-key-terminal-wrapper"] {
        width: 100%;
        max-width: 85%;
        clear: both;
        display: flex;
        flex-direction: column;
    }

    /* Common layout for text vertical centering */
    div[class*="st-key-bubble-user-"] > div, 
    div[class*="st-key-bubble-assistant-"] > div {
        display: flex;
        align-items: center; /* PERFECT VERTICAL CENTERING */
        min-height: 48px; 
    }

    /* User Bubble (Pushed to Right) */
    div[class*="st-key-bubble-user-"] {
        margin-left: auto !important;
        margin-right: 0 !important;
        align-items: flex-end;
    }

    div[class*="st-key-bubble-user-"] > div {
        background: linear-gradient(135deg, var(--brand-cyan), var(--brand-blue));
        border-radius: 20px 20px 4px 20px;
        padding: 10px 20px 20px 20px;
        margin-bottom: 15px;
        color: white !important;
        box-shadow: 0 8px 20px rgba(0, 114, 255, 0.25);
        animation: slideInRight 0.4s cubic-bezier(0.25, 0.8, 0.2, 1) forwards;
        transform-origin: bottom right;
        text-align: left;
        width: fit-content;
    }
    div[class*="st-key-bubble-user-"] p { margin: 0; color: white !important; font-size: 1.05rem;}

    /* Assistant Bubble (Pushed to Left) */
    div[class*="st-key-bubble-assistant-"], div[class*="st-key-terminal-wrapper"] {
        margin-right: auto !important;
        margin-left: 0 !important;
        align-items: flex-start;
    }

    div[class*="st-key-bubble-assistant-"] > div {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 20px 20px 20px 4px;
        padding: 10px 20px 20px 20px;
        margin-bottom: 15px;
        color: var(--text-main) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        animation: slideInLeft 0.4s cubic-bezier(0.25, 0.8, 0.2, 1) forwards;
        transform-origin: bottom left;
        text-align: left;
        width: fit-content;
    }
    div[class*="st-key-bubble-assistant-"] p { margin: 0; font-size: 1.05rem; color: var(--text-main) !important;}

    /* ---------- Chat Input Container ---------- */
    [data-testid="stChatInput"] {
        background: transparent !important;
        padding-bottom: 1rem;
    }
    [data-testid="stChatInput"] textarea {
        border-radius: 24px !important;
        border: 1px solid var(--glass-border) !important;
        background: rgba(20, 24, 39, 0.8) !important;
        backdrop-filter: blur(10px);
        color: white !important;
        padding: 1rem 1.2rem !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--brand-cyan) !important;
        box-shadow: 0 0 0 2px rgba(0, 198, 255, 0.2) !important;
    }
    [data-testid="stChatInput"] button {
        background: var(--brand-blue) !important;
        border-radius: 50% !important;
        transition: transform 0.2s ease !important;
    }
    [data-testid="stChatInput"] button:hover {
        transform: scale(1.1);
        background: var(--brand-cyan) !important;
    }

    /* ---------- Floating Clear Button (Top Right) ---------- */
    div[class*="st-key-clear-btn-container"] {
        position: fixed;
        top: 20px;
        right: 20px;
        width: auto;
        z-index: 1000;
        animation: fadeIn 1s ease-out;
    }

    div[class*="st-key-clear-btn-container"] button {
        border-radius: 30px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(10, 13, 22, 0.5) !important;
        backdrop-filter: blur(8px);
        color: var(--text-muted) !important;
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem !important;
        padding: 0.3rem 0.8rem !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    div[class*="st-key-clear-btn-container"] button:hover {
        border-color: var(--brand-pink) !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(248, 87, 166, 0.4) !important;
        transform: translateY(-2px);
    }

    /* ---------- Live Terminal Box ---------- */
    .terminal-box {
        background: rgba(10, 13, 22, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        margin-bottom: 15px;
        width: 100%;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 198, 255, 0.1);
        animation: fadeIn 0.4s ease-out, borderPulse 2s infinite;
        text-align: left;
    }
    .terminal-header {
        background: rgba(255,255,255,0.03);
        padding: 8px 12px;
        display: flex;
        gap: 6px;
        border-bottom: 1px solid var(--glass-border);
    }
    .mac-dot { width: 10px; height: 10px; border-radius: 50%; }
    .mac-dot.red { background: #ff5f56; }
    .mac-dot.yellow { background: #ffbd2e; }
    .mac-dot.green { background: #27c93f; }

    .terminal-body {
        padding: 12px;
        max-height: 250px;
        overflow-y: auto;
        font-family: 'Fira Code', monospace;
        font-size: 0.85rem;
        color: var(--brand-cyan);
        display: flex;
        flex-direction: column;
        gap: 4px;
        text-align: left;
    }
    .terminal-line {
        line-height: 1.4;
        word-break: break-all;
        text-align: left;
    }
    .terminal-cursor {
        display: inline-block;
        width: 8px; height: 1em;
        background: var(--brand-pink);
        vertical-align: middle;
        animation: blink 1s step-end infinite;
    }

    /* ---------- Animations ---------- */
    @keyframes pulseLogo {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.8; }
    }
    @keyframes borderPulse {
        0%, 100% { border-color: rgba(255, 255, 255, 0.1); }
        50% { border-color: rgba(0, 198, 255, 0.4); }
    }
    @keyframes textShine {
        0% { background-position: 0% center; }
        100% { background-position: -300% center; }
    }
    @keyframes slideInRight {
        0% { opacity: 0; transform: translateX(30px) scale(0.95); }
        100% { opacity: 1; transform: translateX(0) scale(1); }
    }
    @keyframes slideInLeft {
        0% { opacity: 0; transform: translateX(-30px) scale(0.95); }
        100% { opacity: 1; transform: translateX(0) scale(1); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes blink { 50% { opacity: 0; } }

    /* Scrollbar styling for terminal */
    .terminal-body::-webkit-scrollbar { width: 6px; }
    .terminal-body::-webkit-scrollbar-track { background: transparent; }
    .terminal-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 10px; }
</style>
""")

# ==================================================================
# 2. Context-aware Stdout Capture (For Live Terminal)
# ==================================================================
_real_stdout = sys.stdout
# Create a context variable to hold the queue
_log_queue_var = contextvars.ContextVar("log_queue", default=None)


class _ContextAwareStdout:
    def write(self, text: str) -> int:
        # Retrieve the queue from the current async context
        q = _log_queue_var.get()

        if q is not None:
            if text.strip():
                q.put(text)
        else:
            _real_stdout.write(text)
        return len(text)

    def flush(self) -> None:
        _real_stdout.flush()


if not isinstance(sys.stdout, _ContextAwareStdout):
    sys.stdout = _ContextAwareStdout()


def run_agent_with_live_log(prompt: str, log_queue: queue.Queue) -> str:
    # Set the queue in the context variable.
    # This automatically propagates to all child asyncio tasks!
    token = _log_queue_var.set(log_queue)
    try:
        # Calls your Langchain/Pydantic tracker agent
        return asyncio.run(tracker_agent(prompt))
    except Exception as e:
        return f"Agent Error: {str(e)}"
    finally:
        # Clean up the context variable when done
        _log_queue_var.reset(token)


# ==================================================================
# 3. Header & Floating Utilities
# ==================================================================
st.html("""
<div class="header-container">
    <div class="logo-wrapper">
        <span class="target-icon">🎯</span>
        <h1 class="brand-title">ApplyTrack AI</h1>
    </div>
    <p class="brand-subtitle">Automating your job hunt sheet, intelligently.</p>
</div>
""")

# Floating Clear Button placed nicely at top-right
with st.container(key="clear-btn-container"):
    if st.button("🗑️ Clear Chat", use_container_width=False):
        st.session_state.messages = []
        st.rerun()

# ==================================================================
# 4. Session State & Chat Rendering
# ==================================================================
if "messages" not in st.session_state:
    st.session_state.messages = []


def render_bubble(role: str, content: str, key: str):
    # The CSS handles the left/right push automatically based on the key name!
    with st.container(key=key):
        st.markdown(content)


# Render past history
for i, msg in enumerate(st.session_state.messages):
    render_bubble(msg["role"], msg["content"], key=f"bubble-{msg['role']}-{i}")


# ==================================================================
# 5. Live Execution & Chat Input
# ==================================================================
def render_terminal(placeholder, logs: list):
    lines_html = "".join([f'<div class="terminal-line">>&nbsp;{html.escape(line)}</div>' for line in logs])
    html_content = f"""
    <div class="terminal-box">
        <div class="terminal-header">
            <div class="mac-dot red"></div>
            <div class="mac-dot yellow"></div>
            <div class="mac-dot green"></div>
        </div>
        <div class="terminal-body" id="term-body">
            {lines_html}
            <div class="terminal-line"><span class="terminal-cursor"></span></div>
        </div>
        <script>
            var tb = document.getElementById("term-body");
            if(tb) tb.scrollTop = tb.scrollHeight;
        </script>
    </div>
    """
    placeholder.html(html_content)


def stream_final_response(text: str):
    """Simulates a smooth typewriter effect for the final text output"""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.03)


prompt = st.chat_input("Tell ApplyTrack what you applied for today...")

if prompt:
    # 1. Append & render User message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_bubble("user", prompt, key=f"bubble-user-{len(st.session_state.messages)}")

    # 2. Setup Agent processing block aligned to the Left (Assistant side)
    with st.container(key="terminal-wrapper"):
        terminal_placeholder = st.empty()

        log_queue = queue.Queue()
        collected_logs = ["Initializing Tracker Agent..."]
        render_terminal(terminal_placeholder, collected_logs)

        # Run agent in background and capture live logs
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(run_agent_with_live_log, prompt, log_queue)

            while not future.done():
                try:
                    # Get new log lines (non-blocking)
                    line = log_queue.get(timeout=0.1)
                    collected_logs.append(line)
                    render_terminal(terminal_placeholder, collected_logs)
                except queue.Empty:
                    pass

            final_response = future.result()

        # 3. Cleanup terminal & stream the final response into a new chat bubble
        terminal_placeholder.empty()

    with st.container(key=f"bubble-assistant-{len(st.session_state.messages)}"):
        st.write_stream(stream_final_response(final_response))

    # 4. Save to state (no rerun needed because write_stream naturally displays it)
    st.session_state.messages.append({"role": "assistant", "content": final_response})