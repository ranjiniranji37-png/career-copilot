# 🎯 Career Copilot – GenAI Capstone

AI career assistant: **Mock Interview · Resume Improver (ATS) · Cover Letter · Skill Gap Planner · Career Chat**.

| Requirement | Where |
|---|---|
| LLM API integration | `agent.py` (Anthropic Messages API) |
| Prompt engineering | `prompts.py` (role prompts, structured output, few-shot) |
| RAG | `rag.py` (chunking + TF-IDF + cosine retrieval over resume/JD) |
| Tools | `tools.py` (`search_documents`, `ats_match_score`, `skill_gap_plan`) |
| Agent | `agent.py` (reason → tool call → observe loop, max 6 steps) |
| UI | `app.py` (Streamlit) |

Architecture: see [ARCHITECTURE.md](ARCHITECTURE.md).

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your ANTHROPIC_API_KEY
streamlit run app.py
```
Tick **"Use sample resume + JD"** to try it instantly, or upload your own PDF/TXT.

## Deploy (free) – Streamlit Community Cloud
1. Push this folder to a public GitHub repo.
2. Go to https://share.streamlit.io → **New app** → select repo, main file `app.py`.
3. **Advanced settings → Secrets**: `ANTHROPIC_API_KEY = "your_key"`.
4. Deploy → copy the live URL for submission.

## Docker
```bash
docker build -t career-copilot . && docker run -p 8501:8501 -e ANTHROPIC_API_KEY=xxx career-copilot
```

## Demo video checklist
Mock Interview with sample data → Resume Improver (show the tool-call expander) → Skill Gap Planner.

## Ideas to extend
Embedding-based RAG (FAISS/Chroma), streaming responses, voice interview, PDF export.
