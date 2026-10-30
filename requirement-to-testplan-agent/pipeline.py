"""Requirements-to-test-plan workflow: extract -> generate -> coverage check -> flag gaps -> route."""
import json, time, pathlib, argparse
from llm import get_llm

ROOT = pathlib.Path(__file__).parent
CASE_KEYS = {"case_id", "req_id", "type", "steps", "expected"}

def load_prompt(version, stage):
    return (ROOT / "prompts" / version / f"{stage}.md").read_text()

def log(run_id, event):
    event["run_id"] = run_id; event["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(ROOT / "logs" / "runs.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")

def check_schema(cases):
    return all(CASE_KEYS <= set(c) for c in cases)

def run(spec_path, version="v1", mode="mock"):
    llm = get_llm(mode)
    spec = pathlib.Path(spec_path).read_text()
    run_id = f"{pathlib.Path(spec_path).stem}-{version}-{int(time.time()*1000)%100000}"
    reasons = []
    try:
        reqs = llm.complete("extract", load_prompt(version, "extract"), {"spec": spec})["requirements"]
        log(run_id, {"stage": "extract", "n": len(reqs)})
        cases = llm.complete("generate", load_prompt(version, "generate"), {"requirements": reqs})["cases"] if reqs else []
        log(run_id, {"stage": "generate", "n": len(cases)})
        # Stage 3: programmatic coverage + schema check (no model needed)
        covered = {c["req_id"] for c in cases}
        uncovered = [r["id"] for r in reqs if r["id"] not in covered]
        schema_ok = check_schema(cases)
        log(run_id, {"stage": "coverage", "uncovered": uncovered, "schema_ok": schema_ok})
        gaps = llm.complete("gaps", load_prompt(version, "gaps"), {"requirements": reqs})["gaps"] if reqs else []
        log(run_id, {"stage": "gaps", "gaps": gaps})
    except Exception as e:  # any failure goes to a human, never silently passes
        log(run_id, {"stage": "error", "error": str(e)})
        return {"run_id": run_id, "route": "human_review", "reasons": [f"pipeline error: {e}"],
                "requirements": [], "cases": [], "gaps": [], "schema_ok": False}
    if not reqs: reasons.append("no requirements found")
    if uncovered: reasons.append(f"uncovered requirements: {uncovered}")
    if not schema_ok: reasons.append("invalid test case schema")
    if gaps: reasons.append(f"{len(gaps)} requirement gap(s) flagged")
    route = "human_review" if reasons else "auto_approve"
    log(run_id, {"stage": "route", "route": route, "reasons": reasons})
    return {"run_id": run_id, "route": route, "reasons": reasons, "requirements": reqs,
            "cases": cases, "gaps": gaps, "schema_ok": schema_ok}

def to_markdown(spec_name, res):
    out = [f"# Test plan: {spec_name}", f"Route: **{res['route']}**", ""]
    out += [f"- Review reason: {r}" for r in res["reasons"]] or ["- No issues flagged"]
    out += ["", "## Gaps"] + ([f"- {g['req_id']}: {g['issue']}" for g in res["gaps"]] or ["- None"])
    out += ["", "## Test cases", "| ID | Req | Type | Steps | Expected |", "|---|---|---|---|---|"]
    out += [f"| {c['case_id']} | {c['req_id']} | {c['type']} | {c['steps']} | {c['expected']} |" for c in res["cases"]]
    return "\n".join(out) + "\n"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("--version", default="v2"); ap.add_argument("--mode", default="mock")
    a = ap.parse_args()
    res = run(a.spec, a.version, a.mode)
    p = ROOT / "outputs" / f"{pathlib.Path(a.spec).stem}_{a.version}.md"
    p.write_text(to_markdown(pathlib.Path(a.spec).name, res)); print(p, res["route"])
