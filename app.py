import asyncio
import streamlit as st
from src.agent.tracker import tracker_agent

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="ApplyTrack AI",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------
# Styling
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f1117 0%, #1a1d29 100%);
    }
    .hero {
        text-align: center;
        padding: 1.2rem 0 0.4rem 0;
    }
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7C3AED, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero p {
        color: #9CA3AF;
        font-size: 0.95rem;
        margin-top: 0.2rem;
    }
    [data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 0.4rem 0.2rem;
    }
    .stChatInput textarea {
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Hero header
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🎯 ApplyTrack AI</h1>
        <p>Your AI-powered job application tracker</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.subheader("⚙️ Session")
    st.caption(f"Messages this session: {len(st.session_state.get('messages', []))}")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Try asking things like:")
    st.caption("• *Add a new application to Google*")
    st.caption("• *Show me all pending interviews*")
    st.caption("• *Mark the Amazon application as rejected*")

# ------------------------------------------------------------------
# Chat state
# ------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🎯"):
        st.markdown(msg["content"])

# ------------------------------------------------------------------
# Async helper to run the tracker agent from sync Streamlit code
# ------------------------------------------------------------------
def run_agent(prompt: str) -> str:
    return asyncio.run(tracker_agent(prompt))

# ------------------------------------------------------------------
# Chat input
# ------------------------------------------------------------------
if prompt := st.chat_input("Ask ApplyTrack AI to manage your applications..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎯"):
        with st.spinner("Thinking..."):
            try:
                response = run_agent(prompt)
            except Exception as e:
                response = f"⚠️ Something went wrong: `{e}`"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

if not st.session_state.messages:
    st.info("👋 Start by typing a task below — e.g. *\"Add my Netflix application, status: applied\"*", icon="💡")