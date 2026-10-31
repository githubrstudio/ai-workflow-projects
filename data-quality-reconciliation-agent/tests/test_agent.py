import json, pathlib, tempfile, unittest, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from dq_agent import pipeline, reconcile, normalize, extract

class T(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize.to_number("$1,234.50"), 1234.5)
        self.assertEqual(normalize.to_number("(10.00)"), -10.0)
        self.assertEqual(normalize.to_date("03/05/2024"), "2024-03-05")
        self.assertTrue(normalize.is_null(" N/A "))

    def test_mismatch_scenario_counts(self):
        with tempfile.TemporaryDirectory() as d:
            s = pipeline.run(ROOT / "configs/mismatch_scenario.json", d)
            self.assertEqual(s["status"], "REVIEW_REQUIRED")
            c = s["mismatches_by_type"]
            self.assertEqual(c["MISSING_IN_TARGET"], 3)
            self.assertEqual(c["EXTRA_IN_TARGET"], 2)
            self.assertEqual(c["DUPLICATE_KEY_TARGET"], 1)
            self.assertEqual(c["NULL_MISMATCH"], 2)
            self.assertEqual(c["FORMAT_DIFFERENCE"], 5)      # 2 case, 2 date format, 1 whitespace
            self.assertTrue((pathlib.Path(d) / "mismatches.csv").exists())

    def test_match_scenario_writes_summary_only(self):
        with tempfile.TemporaryDirectory() as d:
            s = pipeline.run(ROOT / "configs/match_scenario.json", d)
            self.assertEqual(s["status"], "MATCH"); self.assertEqual(s["total_mismatches"], 0)
            self.assertTrue((pathlib.Path(d) / "summary_counts.json").exists())
            self.assertFalse((pathlib.Path(d) / "mismatches.csv").exists())

    def test_tolerance(self):
        cfg = {"keys": [{"source": "k", "target": "k"}], "columns": [{"name": "v", "source": "v", "target": "v", "type": "numeric", "tolerance": 0.5}]}
        self.assertEqual(reconcile.reconcile([{"k": "1", "v": "10.0"}], [{"k": "1", "v": "10.4"}], cfg), [])
        self.assertEqual(len(reconcile.reconcile([{"k": "1", "v": "10.0"}], [{"k": "1", "v": "10.6"}], cfg)), 1)

    def test_missing_column_fails_loudly(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "x.csv"; p.write_text("a,b\n1,2\n")
            with self.assertRaises(extract.ExtractError): extract.load_csv(p, ["a", "zzz"])

if __name__ == "__main__": unittest.main()
