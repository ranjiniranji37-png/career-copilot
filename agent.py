"""Tool-using agent loop on the Anthropic Messages API (LLM API integration)."""
import os

import anthropic

from tools import TOOL_SCHEMAS, ToolBox

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_STEPS = 6


def make_client(api_key: str | None = None) -> anthropic.Anthropic:
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("Missing ANTHROPIC_API_KEY")
    return anthropic.Anthropic(api_key=key)


def run_agent(client, system: str, history: list[dict], toolbox: ToolBox,
              model: str = DEFAULT_MODEL, max_steps: int = MAX_STEPS):
    """Reason -> call tools -> observe -> repeat. Returns (answer, trace)."""
    messages = [dict(m) for m in history]
    trace = []
    for _ in range(max_steps):
        resp = client.messages.create(
            model=model, max_tokens=1500, system=system,
            tools=TOOL_SCHEMAS, messages=messages,
        )
        if resp.stop_reason != "tool_use":
            text = "".join(b.text for b in resp.content if b.type == "text")
            return text, trace

        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                out = toolbox.run(block.name, block.input)
                trace.append({"tool": block.name, "input": block.input, "output": out})
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": out})
        messages.append({"role": "user", "content": results})
    return "I reached the step limit. Please try a more specific question.", trace
