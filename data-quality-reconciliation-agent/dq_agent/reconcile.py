"""Stage 3 - Reconcile: row-level comparison keyed on the business key."""
import collections
from .normalize import is_null, to_number, to_date, norm_key

def _key(row, cols, ci): return tuple(norm_key(row.get(c), ci) for c in cols)

def _index(rows, cols, ci):
    idx, dups = {}, collections.defaultdict(list)
    for i, r in enumerate(rows):
        k = _key(r, cols, ci)
        if k in idx: dups[k].append(i)
        else: idx[k] = r
    return idx, dups

def _compare_value(m, a, b):
    """Return None if equal, else (mismatch_type, detail)."""
    an, bn = is_null(a), is_null(b)
    if an and bn: return None
    if an != bn: return ("NULL_MISMATCH", "")
    kind = m.get("type", "string")
    if kind == "numeric":
        x, y = to_number(a), to_number(b)
        if x is None or y is None: return ("VALUE_MISMATCH", "non-numeric value")
        if abs(x - y) <= m.get("tolerance", 0.0): return None
        return ("VALUE_MISMATCH", f"diff={round(y - x, 4)}")
    if kind == "date":
        x, y = to_date(a), to_date(b)
        if x is None or y is None: return ("VALUE_MISMATCH", "unparseable date")
        if x == y: return None if str(a).strip() == str(b).strip() else ("FORMAT_DIFFERENCE", "same date, different format")
        return ("VALUE_MISMATCH", f"{x} vs {y}")
    if str(a) == str(b): return None
    if str(a).strip() == str(b).strip(): return ("FORMAT_DIFFERENCE", "whitespace only")
    if str(a).strip().casefold() == str(b).strip().casefold(): return ("FORMAT_DIFFERENCE", "case only")
    return ("VALUE_MISMATCH", "")

def reconcile(src_rows, tgt_rows, cfg):
    ci = cfg.get("key_case_insensitive", True)
    skeys = [k["source"] for k in cfg["keys"]]; tkeys = [k["target"] for k in cfg["keys"]]
    sidx, sdups = _index(src_rows, skeys, ci); tidx, tdups = _index(tgt_rows, tkeys, ci)
    out = []
    show = {}
    for r in tgt_rows: show[_key(r, tkeys, ci)] = "|".join(str(r.get(c, "")).strip() for c in tkeys)
    for r in src_rows: show[_key(r, skeys, ci)] = "|".join(str(r.get(c, "")).strip() for c in skeys)   # source spelling wins
    def add(typ, key, col="", sv="", tv="", detail=""):
        out.append({"mismatch_type": typ, "key": show.get(key, "|".join(key)), "column": col, "source_value": sv, "target_value": tv, "detail": detail})
    for k in sdups: add("DUPLICATE_KEY_SOURCE", k, detail=f"{len(sdups[k]) + 1} rows share this key")
    for k in tdups: add("DUPLICATE_KEY_TARGET", k, detail=f"{len(tdups[k]) + 1} rows share this key")
    for k, s in sidx.items():
        t = tidx.get(k)
        if t is None: add("MISSING_IN_TARGET", k); continue
        for m in cfg["columns"]:
            res = _compare_value(m, s.get(m["source"]), t.get(m["target"]))
            if res: add(res[0], k, m["name"], s.get(m["source"]), t.get(m["target"]), res[1])
    for k in tidx:
        if k not in sidx: add("EXTRA_IN_TARGET", k)
    return out
