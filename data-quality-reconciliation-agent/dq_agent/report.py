"""Stage 5 - Report: write human-reviewable outputs. Every run writes summary_counts.*; mismatches.csv only when there is work to review."""
import csv, json, collections, pathlib, datetime

FIELDS = ["severity", "mismatch_type", "key", "column", "source_value", "target_value", "detail", "likely_cause", "review_decision", "reviewer_notes"]

def write_outputs(out_dir, cfg, src_n, tgt_n, profile_rows, mismatches, now=None):
    d = pathlib.Path(out_dir); d.mkdir(parents=True, exist_ok=True)
    now = now or datetime.datetime.now().isoformat(timespec="seconds")
    by_type = collections.Counter(m["mismatch_type"] for m in mismatches)
    by_sev = collections.Counter(m["severity"] for m in mismatches)
    by_col = collections.Counter(m["column"] for m in mismatches if m["column"])
    flagged = [r for r in profile_rows if r["flag"]]
    status = "MATCH" if not mismatches and not flagged else "REVIEW_REQUIRED"
    summary = {"run_name": cfg.get("name", "reconciliation"), "run_time": now, "status": status,
               "source_rows": src_n, "target_rows": tgt_n, "total_mismatches": len(mismatches),
               "mismatches_by_type": dict(by_type), "mismatches_by_severity": dict(by_sev), "mismatches_by_column": dict(by_col),
               "profile_metrics_checked": len(profile_rows), "profile_metrics_flagged": len(flagged)}
    (d / "summary_counts.json").write_text(json.dumps(summary, indent=2))
    with open(d / "profile_comparison.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["column", "metric", "source", "target", "delta", "flag"]); w.writeheader(); w.writerows(profile_rows)
    md = [f"# Reconciliation summary: {summary['run_name']}", f"Run: {now}  |  Status: **{status}**", "",
          f"- Source rows: {src_n}", f"- Target rows: {tgt_n}", f"- Total mismatches: {len(mismatches)}",
          f"- Profile metrics flagged: {len(flagged)} of {len(profile_rows)}", ""]
    if mismatches:
        md += ["## Mismatches by type"] + [f"- {k}: {v}" for k, v in sorted(by_type.items())]
        md += ["", "## By severity"] + [f"- {k}: {v}" for k, v in sorted(by_sev.items())]
        md += ["", "## By column"] + [f"- {k}: {v}" for k, v in sorted(by_col.items())]
        md += ["", "Next step: a person reviews `mismatches.csv` and fills `review_decision` and `reviewer_notes`."]
        with open(d / "mismatches.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(sorted(mismatches, key=lambda m: ("high", "medium", "low").index(m["severity"])))
    else:
        md += ["Both datasets match on keys and compared columns, and profile metrics are within tolerance.", "No review queue was created."]
        stale = d / "mismatches.csv"
        if stale.exists(): stale.unlink()
    (d / "summary_counts.md").write_text("\n".join(md) + "\n")
    return summary
