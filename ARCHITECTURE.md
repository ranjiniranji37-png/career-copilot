# Architecture

![diagram](architecture.svg)

```mermaid
flowchart LR
  U[User - Streamlit UI] --> A[Agent loop]
  P[Prompts: role + few-shot] --> A
  A <--> L[Claude API - tool use]
  A --> T[Tools]
  T --> R[RAG: TF-IDF retrieval]
  R --> D[(Resume + JD)]
  T --> S[ATS score / Skill gap plan]
```

**Flow:** the UI sends chat history + mode prompt to the agent. The agent calls Claude with tool
schemas; when Claude requests a tool, we run it (RAG search, ATS scoring, gap planning), feed the
result back, and loop until Claude returns the final answer (max 6 steps).
