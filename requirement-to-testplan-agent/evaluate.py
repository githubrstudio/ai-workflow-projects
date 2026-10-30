"""Score a prompt version against the eval set; compare versions side by side."""
import json, sys, pathlib
from pipeline import run, ROOT

def score(version, mode):
    rows = json.loads((ROOT / "data" / "eval_set.json").read_text())
    res = []
    for e in rows:
        r = run(ROOT / "data" / "specs" / e["spec"], version, mode)
        got = {g["req_id"] for g in r["gaps"]}; exp = set(e["gaps"])
        res.append({"spec": e["spec"], "extract_ok": len(r["requirements"]) == e["n_reqs"],
                    "gap_tp": len(got & exp), "gap_fp": len(got - exp), "gap_fn": len(exp - got),
                    "route_ok": r["route"] == e["route"], "schema_ok": r["schema_ok"],
                    "cases": len(r["cases"])})
    tp = sum(x["gap_tp"] for x in res); fp = sum(x["gap_fp"] for x in res); fn = sum(x["gap_fn"] for x in res)
    n = len(res)
    return {"version": version, "mode": mode, "extraction_acc": sum(x["extract_ok"] for x in res)/n,
            "gap_precision": tp/(tp+fp) if tp+fp else 1.0, "gap_recall": tp/(tp+fn) if tp+fn else 1.0,
            "routing_acc": sum(x["route_ok"] for x in res)/n, "schema_valid": sum(x["schema_ok"] for x in res)/n,
            "total_cases": sum(x["cases"] for x in res), "detail": res}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "mock"
    out = [score(v, mode) for v in ("v1", "v2")]
    (ROOT / "results" / f"eval_{mode}.json").write_text(json.dumps(out, indent=2))
    print(f"{'metric':<16}{'v1':>8}{'v2':>8}")
    for k in ("extraction_acc", "gap_precision", "gap_recall", "routing_acc", "schema_valid", "total_cases"):
        print(f"{k:<16}{out[0][k]:>8.2f}{out[1][k]:>8.2f}")
    for o in out:
        for d in o["detail"]:
            if not (d["extract_ok"] and d["route_ok"] and d["gap_fp"] == 0 and d["gap_fn"] == 0):
                print("miss", o["version"], d["spec"], d)
