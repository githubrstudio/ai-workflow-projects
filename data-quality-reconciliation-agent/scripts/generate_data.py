"""Generate synthetic account data. No real customers or institutions. Deterministic (seeded)."""
import csv, random, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent / "data"
FIRST = ["Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Avery", "Quinn"]
LAST = ["Nguyen", "Patel", "Garcia", "Kim", "Okafor", "Silva", "Novak", "Haddad", "Larsen", "Mori"]
BRANCHES = ["PHX01", "PHX02", "TUS01", "FLG01", "MSA01"]
STATUS = ["Active", "Dormant", "Closed"]

def make_source(n=200, seed=42):
    rng = random.Random(seed); rows = []
    for i in range(1, n + 1):
        d = datetime.date(2015, 1, 1) + datetime.timedelta(days=rng.randint(0, 3600))
        rows.append({"account_id": f"AC{i:05d}", "customer_name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                     "balance": f"{rng.uniform(50, 90000):.2f}", "open_date": d.isoformat(),
                     "status": rng.choice(STATUS), "branch": rng.choice(BRANCHES)})
    return rows

def to_target(rows):
    return [{"acct_id": r["account_id"], "cust_name": r["customer_name"], "current_balance": r["balance"],
             "opened_on": r["open_date"], "acct_status": r["status"], "branch_code": r["branch"]} for r in rows]

def inject_defects(t):
    t = [dict(r) for r in t]
    def row(i): return t[i]
    for i in (5, 60, 150): t[i]["acct_id"] = "__DROP__"                               # 3 missing in target
    t = [r for r in t if r["acct_id"] != "__DROP__"]
    for i in (10, 20, 30, 40): row(i)["current_balance"] = f"{float(row(i)['current_balance']) + 0.4:.2f}"   # rounding-size diffs
    for i in (15, 25): row(i)["current_balance"] = f"{-float(row(i)['current_balance']):.2f}"                # sign flips
    for i in (50, 70, 90): row(i)["current_balance"] = f"{float(row(i)['current_balance']) * 10:.2f}"        # scale errors
    for i in (100, 110): row(i)["acct_status"] = row(i)["acct_status"].upper()                               # case only
    for i in (120, 130):                                                                                      # date format only
        y, m, d = row(i)["opened_on"].split("-"); row(i)["opened_on"] = f"{m}/{d}/{y}"
    for i in (140, 145): row(i)["current_balance"] = ""                                                      # nulls
    for i in (160, 170): row(i)["branch_code"] = "PHX99"                                                     # changed value
    row(180)["cust_name"] = row(180)["cust_name"] + "  "                                                     # whitespace only
    t.append({"acct_id": "AC90001", "cust_name": "Extra One", "current_balance": "100.00", "opened_on": "2024-01-01", "acct_status": "Active", "branch_code": "PHX01"})
    t.append({"acct_id": "AC90002", "cust_name": "Extra Two", "current_balance": "250.00", "opened_on": "2024-02-01", "acct_status": "Active", "branch_code": "TUS01"})
    t.append(dict(t[0]))                                                                                      # duplicate key in target
    return t

def reformat_equivalent(t):
    """Same values, different presentation: should still reconcile as MATCH."""
    out = []
    for r in t:
        r = dict(r); r["current_balance"] = f"${float(r['current_balance']):,.2f}"; r["acct_id"] = r["acct_id"].lower(); out.append(r)
    return out

def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    src = make_source(); tgt = to_target(src)
    write(ROOT / "mismatch_scenario/source_accounts.csv", src)
    write(ROOT / "mismatch_scenario/reporting_accounts.csv", inject_defects(tgt))
    write(ROOT / "match_scenario/source_accounts.csv", src)
    write(ROOT / "match_scenario/reporting_accounts.csv", reformat_equivalent(tgt))
    print("synthetic data written to", ROOT)
