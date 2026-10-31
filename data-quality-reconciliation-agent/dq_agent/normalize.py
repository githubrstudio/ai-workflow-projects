"""Value parsing shared by profiling and reconciliation."""
import re, datetime

DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y", "%Y/%m/%d", "%m-%d-%Y")

def is_null(v):
    return v is None or str(v).strip().lower() in ("", "null", "none", "nan", "n/a")

def to_number(v):
    if is_null(v): return None
    s = str(v).strip()
    neg = s.startswith("(") and s.endswith(")")
    s = re.sub(r"[,$()\s]", "", s)
    try: x = float(s)
    except ValueError: return None
    return -x if neg else x

def to_date(v):
    if is_null(v): return None
    s = str(v).strip()
    for fmt in DATE_FORMATS:
        try: return datetime.datetime.strptime(s, fmt).date().isoformat()
        except ValueError: pass
    return None

def norm_key(v, case_insensitive=True):
    s = "" if v is None else str(v).strip()
    return s.casefold() if case_insensitive else s
