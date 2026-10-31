"""Stage 2 - Statistical analysis: profile both datasets and compare the profiles."""
import statistics, collections
from .normalize import is_null, to_number

def profile(rows, columns):
    out = {"row_count": len(rows), "columns": {}}
    for c in columns:
        vals = [r.get(c) for r in rows]
        nonnull = [v for v in vals if not is_null(v)]
        p = {"nulls": len(vals) - len(nonnull), "distinct": len(set(nonnull))}
        nums = [to_number(v) for v in nonnull]
        if nonnull and all(n is not None for n in nums):
            p.update({"kind": "numeric", "sum": round(sum(nums), 4), "mean": round(statistics.fmean(nums), 4),
                      "stdev": round(statistics.pstdev(nums), 4), "min": min(nums), "max": max(nums)})
        else:
            top = collections.Counter(str(v).strip() for v in nonnull).most_common(3)
            p.update({"kind": "text", "top_values": top})
        out["columns"][c] = p
    return out

def compare_profiles(src, tgt, mapping, tolerance_pct=0.0):
    """Return rows of metric deltas and a flag when a delta exceeds tolerance_pct (relative)."""
    rows = [{"column": "(row_count)", "metric": "row_count", "source": src["row_count"], "target": tgt["row_count"],
             "delta": tgt["row_count"] - src["row_count"], "flag": src["row_count"] != tgt["row_count"]}]
    for m in mapping:
        s, t = src["columns"][m["source"]], tgt["columns"][m["target"]]
        metrics = ["nulls", "distinct"] + (["sum", "mean", "stdev", "min", "max"] if s["kind"] == t["kind"] == "numeric" else [])
        for k in metrics:
            a, b = s[k], t[k]
            delta = round(b - a, 4)
            rel = abs(delta) / abs(a) * 100 if a else (0 if delta == 0 else 100)
            rows.append({"column": m["name"], "metric": k, "source": a, "target": b, "delta": delta, "flag": rel > tolerance_pct})
    return rows
