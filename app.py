"""Career Copilot - GenAI Capstone (Streamlit UI)."""
import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from agent import DEFAULT_MODEL, make_client, run_agent
from prompts import MODES
from rag import KnowledgeBase
from tools import ToolBox

load_dotenv()
st.set_page_config(page_title="Career Copilot", page_icon="🎯", layout="wide")
DATA = Path(__file__).parent


def read_upload(f) -> str:
    if f.name.lower().endswith(".pdf"):
        return "\n".join(p.extract_text() or "" for p in PdfReader(f).pages)
    return f.read().decode("utf-8", errors="ignore")


def get_key() -> str | None:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return st.session_state.get("key_input") or os.getenv("GEMINI_API_KEY")


# ---------- Sidebar ----------
with st.sidebar:
    st.title("🎯 Career Copilot")
    st.text_input("Gemini API key", type="password", key="key_input",
                  help="Not needed if set in env / Streamlit secrets.")
    mode = st.selectbox("Mode", list(MODES))
    resume_f = st.file_uploader("Resume (PDF/TXT)", type=["pdf", "txt"])
    jd_f = st.file_uploader("Job description (PDF/TXT)", type=["pdf", "txt"])
    use_sample = st.checkbox("Use sample resume + JD", value=not (resume_f and jd_f))
    if st.button("Clear chat"):
        st.session_state.messages = []

if use_sample:
    resume = (DATA / "sample_resume.txt").read_text()
    jd = (DATA / "sample_jd.txt").read_text()
else:
    resume = read_upload(resume_f) if resume_f else ""
    jd = read_upload(jd_f) if jd_f else ""

# ---------- Build RAG index ----------
kb = KnowledgeBase()
if resume:
    kb.add_document("resume", resume)
if jd:
    kb.add_document("job_description", jd)
toolbox = ToolBox(kb, resume, jd)

# ---------- Chat ----------
st.header(f"{mode}")
st.session_state.setdefault("messages", [])
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ask something, or type 'start' for the mock interview..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            client = make_client(get_key())
            with st.spinner("Thinking..."):
                answer, trace = run_agent(client, MODES[mode], st.session_state.messages,
                                          toolbox, DEFAULT_MODEL)
            st.markdown(answer)
            if trace:
                with st.expander(f"🛠 Agent used {len(trace)} tool call(s)"):
                    for t in trace:
                        st.code(f"{t['tool']}({json.dumps(t['input'])})\n→ {t['output'][:600]}")
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Error: {e}")
