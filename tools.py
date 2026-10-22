"""Tools the agent can call (function calling / tool use)."""
import json
import re

from rag import KnowledgeBase

SKILL_VOCAB = {
    "python", "java", "javascript", "typescript", "c++", "sql", "html", "css", "react",
    "node.js", "django", "flask", "fastapi", "streamlit", "git", "github", "docker",
    "kubernetes", "aws", "azure", "gcp", "linux", "rest", "api", "machine learning",
    "deep learning", "nlp", "llm", "rag", "prompt engineering", "langchain", "pandas",
    "numpy", "scikit-learn", "tensorflow", "pytorch", "mongodb", "postgresql", "mysql",
    "ci/cd", "agile", "data structures", "algorithms", "communication", "problem solving",
}


def extract_skills(text: str) -> set[str]:
    low = text.lower()
    return {s for s in SKILL_VOCAB
            if re.search(r"(?<![a-z0-9+#])" + re.escape(s) + r"(?![a-z0-9+#])", low)}


TOOL_SCHEMAS = [
    {
        "name": "search_documents",
        "description": "Semantic search (RAG) over the user's uploaded resume and job description. "
                       "Use it to ground answers in the user's real experience.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"},
                           "top_k": {"type": "integer", "default": 3}},
            "required": ["query"],
        },
    },
    {
        "name": "ats_match_score",
        "description": "Compute an ATS-style keyword match score (0-100) between the resume and the "
                       "job description, with matched and missing skills.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "skill_gap_plan",
        "description": "Given missing skills, return a prioritized learning plan with estimated days.",
        "input_schema": {
            "type": "object",
            "properties": {"missing_skills": {"type": "array", "items": {"type": "string"}}},
            "required": ["missing_skills"],
        },
    },
]


class ToolBox:
    def __init__(self, kb: KnowledgeBase, resume: str, jd: str):
        self.kb, self.resume, self.jd = kb, resume, jd

    def run(self, name: str, args: dict) -> str:
        fn = getattr(self, f"_{name}", None)
        if fn is None:
            return json.dumps({"error": f"unknown tool {name}"})
        try:
            return json.dumps(fn(**args))
        except Exception as e:  # return errors to the model instead of crashing
            return json.dumps({"error": str(e)})

    def _search_documents(self, query: str, top_k: int = 3):
        return self.kb.search(query, top_k) or {"message": "No relevant content found."}

    def _ats_match_score(self):
        if not self.resume or not self.jd:
            return {"error": "Upload both a resume and a job description first."}
        jd_sk, res_sk = extract_skills(self.jd), extract_skills(self.resume)
        if not jd_sk:
            return {"error": "No recognizable skills found in the job description."}
        matched, missing = sorted(jd_sk & res_sk), sorted(jd_sk - res_sk)
        return {"score": round(100 * len(matched) / len(jd_sk)),
                "matched": matched, "missing": missing}

    def _skill_gap_plan(self, missing_skills: list):
        plan = []
        for i, s in enumerate(missing_skills, 1):
            days = 5 if len(s) <= 4 else 7
            plan.append({"priority": i, "skill": s, "est_days": days,
                         "action": f"Learn core concepts of {s}, then build one mini project using it."})
        return {"plan": plan, "total_days": sum(p["est_days"] for p in plan)}
