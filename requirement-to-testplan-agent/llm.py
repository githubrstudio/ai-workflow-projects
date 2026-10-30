"""LLM backends. MockLLM is a deterministic, rule-based stand-in so the harness runs offline.
Its behavior is driven by the markers in the prompt text, so changing a prompt changes results.
ApiLLM calls a real model (needs the anthropic package and ANTHROPIC_API_KEY)."""
import json, os, re

VAGUE = ["quickly", "fast", "easy", "appropriate", "reasonable", "secure", "user-friendly", "as needed"]

class MockLLM:
    name = "mock"
    def complete(self, stage, system_prompt, payload):
        if stage == "extract":
            reqs = [{"id": m.group(1), "text": m.group(2).strip()}
                    for m in re.finditer(r"^(REQ-\d+):\s*(.+)$", payload["spec"], re.M)]
            return {"requirements": reqs}
        if stage == "generate":
            cases, n = [], 0
            for r in payload["requirements"]:
                def add(t, steps, exp):
                    nonlocal n; n += 1
                    cases.append({"case_id": f"TC-{n:03d}", "req_id": r["id"], "type": t, "steps": steps, "expected": exp})
                add("positive", f"Exercise: {r['text']}", "Requirement is met")
                if "BOUNDARY" in system_prompt and re.search(r"\d", r["text"]):
                    add("boundary", f"Test at and just beyond the limit in: {r['text']}", "Limit enforced exactly")
                if "ADD_NEGATIVE" in system_prompt and re.search(r"\b(reject|only|limit|lock)\b", r["text"], re.I):
                    add("negative", f"Attempt a disallowed action for: {r['text']}", "Action is refused")
            return {"cases": cases}
        if stage == "gaps":
            gaps = []
            for r in payload["requirements"]:
                t = r["text"].lower()
                vague = [w for w in VAGUE if w in t]
                if "FLAG_VAGUE" in system_prompt and vague:
                    gaps.append({"req_id": r["id"], "issue": f"Vague wording: {', '.join(vague)}"})
                elif not re.search(r"\d|pdf|email|error message|\bonly\b|reject", t):
                    gaps.append({"req_id": r["id"], "issue": "No measurable acceptance criteria"})
            return {"gaps": gaps}
        raise ValueError(stage)

class ApiLLM:
    name = "api"
    def __init__(self, model=None):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = model or os.environ.get("R2T_MODEL", "claude-sonnet-5-5")
    def complete(self, stage, system_prompt, payload):
        msg = self.client.messages.create(model=self.model, max_tokens=2000, system=system_prompt,
            messages=[{"role": "user", "content": json.dumps(payload)}])
        text = msg.content[0].text
        m = re.search(r"\{.*\}", text, re.S)
        return json.loads(m.group(0))  # raises if the model returns bad JSON; pipeline logs and routes to review

def get_llm(mode):
    return ApiLLM() if mode == "api" else MockLLM()
