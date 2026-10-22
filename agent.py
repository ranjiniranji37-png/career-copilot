"""Tool-using agent loop on the Google Gemini API (REST, function calling)."""
import os
import time

import requests

from tools import TOOL_SCHEMAS, ToolBox

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
MAX_STEPS = 6
URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def make_client(api_key: str | None = None) -> str:
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Missing GEMINI_API_KEY")
    return key.strip()


def _declarations():
    decls = []
    for t in TOOL_SCHEMAS:
        d = {"name": t["name"], "description": t["description"]}
        props = t["input_schema"].get("properties", {})
        if props:  # Gemini rejects empty parameter objects
            clean = {k: {kk: vv for kk, vv in v.items() if kk != "default"} for k, v in props.items()}
            d["parameters"] = {"type": "object", "properties": clean,
                               "required": t["input_schema"].get("required", [])}
        decls.append(d)
    return [{"function_declarations": decls}]


def _call(key, model, system, contents):
    body = {"system_instruction": {"parts": [{"text": system}]},
            "contents": contents, "tools": _declarations(),
            "generationConfig": {"maxOutputTokens": 1500}}
    r = None
    for attempt in range(5):  # retry on busy / rate-limit errors
        r = requests.post(
            URL.format(model=model),
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json=body, timeout=90,
        )
        if r.status_code in (429, 500, 503) and attempt < 4:
            time.sleep(3 * (attempt + 1))
            continue
        break
    if r.status_code != 200:
        raise RuntimeError(f"Gemini API error {r.status_code}: {r.text[:300]}")
    return r.json()


def run_agent(client, system: str, history: list[dict], toolbox: ToolBox,
              model: str = DEFAULT_MODEL, max_steps: int = MAX_STEPS):
    """Reason -> call tools -> observe -> repeat. Returns (answer, trace)."""
    contents = [{"role": "model" if m["role"] == "assistant" else "user",
                 "parts": [{"text": m["content"]}]} for m in history]
    trace = []
    for _ in range(max_steps):
        data = _call(client, model, system, contents)
        cands = data.get("candidates") or []
        if not cands or "content" not in cands[0]:
            return "No response from the model. Please try again.", trace
        content = cands[0]["content"]
        parts = content.get("parts", [])
        calls = [p["functionCall"] for p in parts if "functionCall" in p]
        if not calls:
            return "".join(p.get("text", "") for p in parts), trace

        contents.append(content)
        responses = []
        for c in calls:
            args = c.get("args", {}) or {}
            out = toolbox.run(c["name"], args)
            trace.append({"tool": c["name"], "input": args, "output": out})
            responses.append({"functionResponse": {"name": c["name"], "response": {"result": out}}})
        contents.append({"role": "user", "parts": responses})
    return "I reached the step limit. Please try a more specific question.", trace
