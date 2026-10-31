import json, pathlib, argparse, sys
from . import extract, profile, reconcile, triage, report

def load_config(path):
    cfg = json.loads(pathlib.Path(path).read_text())
    for k in ("source_file", "target_file", "keys", "columns"):
        if k not in cfg: raise SystemExit(f"Config missing '{k}'")
    for c in cfg["columns"]:
        c.setdefault("name", c["source"])
    return cfg

def run(config_path, out_dir):
    cfg = load_config(config_path)
    base = pathlib.Path(config_path).resolve().parent
    rs = lambda p: (base / p) if not pathlib.Path(p).is_absolute() else pathlib.Path(p)
    scols = [k["source"] for k in cfg["keys"]] + [c["source"] for c in cfg["columns"]]
    tcols = [k["target"] for k in cfg["keys"]] + [c["target"] for c in cfg["columns"]]
    src = extract.load_csv(rs(cfg["source_file"]), scols)
    tgt = extract.load_csv(rs(cfg["target_file"]), tcols)
    sp, tp = profile.profile(src, scols), profile.profile(tgt, tcols)
    mapping = [{"name": c["name"], "source": c["source"], "target": c["target"]} for c in cfg["columns"]]
    prof_rows = profile.compare_profiles(sp, tp, mapping, cfg.get("profile_tolerance_pct", 0.0))
    mism = triage.triage(reconcile.reconcile(src, tgt, cfg))
    return report.write_outputs(out_dir, cfg, len(src), len(tgt), prof_rows, mism)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Reconcile a source dataset against a reporting dataset.")
    ap.add_argument("--config", required=True); ap.add_argument("--out", default="output")
    a = ap.parse_args(argv)
    s = run(a.config, a.out)
    print(f"{s['status']}: {s['total_mismatches']} mismatches ({s['source_rows']} source rows, {s['target_rows']} target rows) -> {a.out}/")
    return 0 if s["status"] == "MATCH" else 1

if __name__ == "__main__": sys.exit(main())
