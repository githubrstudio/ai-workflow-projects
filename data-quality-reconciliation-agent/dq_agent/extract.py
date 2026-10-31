"""Stage 1 - Extract: load a dataset and validate it against the config before any comparison."""
import csv, pathlib

class ExtractError(Exception): pass

def load_csv(path, required_columns):
    p = pathlib.Path(path)
    if not p.exists(): raise ExtractError(f"File not found: {path}")
    with open(p, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        missing = [c for c in required_columns if c not in cols]
        if missing: raise ExtractError(f"{path}: missing required columns {missing}")
        rows = [dict(r) for r in reader]
    return rows
