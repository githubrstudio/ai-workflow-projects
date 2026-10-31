"""Stage 4 - Triage: attach a likely cause and a severity to each mismatch. Rules only; a human decides."""
from .normalize import to_number

SEVERITY = {"MISSING_IN_TARGET": "high", "EXTRA_IN_TARGET": "high", "DUPLICATE_KEY_SOURCE": "high", "DUPLICATE_KEY_TARGET": "high",
            "NULL_MISMATCH": "medium", "VALUE_MISMATCH": "medium", "FORMAT_DIFFERENCE": "low"}

def likely_cause(m):
    t = m["mismatch_type"]
    if t == "MISSING_IN_TARGET": return "Record dropped in the load, filtered out, or not yet loaded"
    if t == "EXTRA_IN_TARGET": return "Record exists only in the reporting table; check late arrivals or deleted source rows"
    if t.startswith("DUPLICATE"): return "Key is not unique; check for double loads or a bad join"
    if t == "NULL_MISMATCH": return "Value lost or defaulted during transformation"
    if t == "FORMAT_DIFFERENCE": return "Formatting difference only; values agree after normalizing"
    a, b = to_number(m["source_value"]), to_number(m["target_value"])
    if a is not None and b is not None:
        if a != 0 and a == -b: return "Sign flip"
        if abs(a - b) <= 1: return "Rounding or truncation"
        if a != 0 and abs(b / a - 1) > 0.5: return "Possible unit or scale error"
        return "Numeric difference; check the transformation or timing of the snapshot"
    return "Value changed between systems; check mapping or a stale copy"

def triage(mismatches):
    for m in mismatches:
        m["severity"] = SEVERITY.get(m["mismatch_type"], "medium")
        m["likely_cause"] = likely_cause(m)
        m["review_decision"] = ""      # human fills: accept / fix_source / fix_target / ignore
        m["reviewer_notes"] = ""
    return mismatches
