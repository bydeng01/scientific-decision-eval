"""Development regressions and synthetic engineering probes, not new science data."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from rules import predict
from run import make_matrix, run, validate_inputs
from score import evaluate

BASE = Path(__file__).resolve().parent


class PreflightChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((BASE/"inputs/cases.json").read_text())
        cls.groups = json.loads((BASE/"inputs/evidence.json").read_text())
        cls.sources = json.loads((BASE/"inputs/sources.json").read_text())
        cls.refs = json.loads((BASE/"evaluation/references.json").read_text())
        cls.budget = json.loads((BASE/"budget.json").read_text())

    def example(self, cid):
        c = deepcopy(next(c for c in self.cases if c["case_id"] == cid))
        text = next(g["evidence_text"] for g in self.groups if g["group_id"] == c["group_id"])
        return c, text

    def all_predictions(self):
        return [predict(*self.example(c["case_id"])) for c in self.cases]

    def test_reviewed_text_predictions_and_separate_oracle(self):
        scores, oracle = evaluate(self.all_predictions(), self.cases, self.refs)
        self.assertEqual(len(oracle), 12)
        for r in scores["per_case"]:
            for k in ("relation_exact", "count_correct", "label_correct", "action_correct", "oracle_count_correct", "oracle_label_correct"):
                self.assertTrue(r[k], (r["case_id"], k))
            self.assertTrue(r.get("engineering_correct", True))

    def test_evidence_matches_english_review(self):
        review = (BASE/"ALL_CASES_REVIEW.md").read_text().split("## 2. Case inputs")[1].split("## 3.")[0]
        for g in self.groups:
            part = review.split("### "+g["group_id"]+": ")[1].split("\n### ")[0]
            self.assertEqual(g["evidence_text"], "\n".join(s[2:] for s in part.splitlines() if s.startswith("> ")))

    @unittest.skipUnless((BASE / "history/zh-preflight-v2").is_dir(),
                         "Private pre-translation archive is not distributed; current English inputs are checked separately")
    def test_translation_preserves_scopes_quantities_and_references(self):
        archive = BASE/"history/zh-preflight-v2"
        old_cases = json.loads((archive/"inputs/cases.json").read_text())
        def nonlinguistic(case):
            case = deepcopy(case)
            for key in ("claim_text", "target_treatment"):
                del case[key]
            del case["scope"]["text"]
            for choice in case.get("engineering", {}).get("choices", []):
                del choice["text"]
            return case
        self.assertEqual([nonlinguistic(c) for c in old_cases], [nonlinguistic(c) for c in self.cases])
        old_groups = json.loads((archive/"inputs/evidence.json").read_text())
        for old, new in zip(old_groups, self.groups):
            self.assertEqual({k: v for k, v in old.items() if k not in ("evidence_text", "evidence_origin")},
                             {k: v for k, v in new.items() if k not in ("evidence_text", "evidence_origin")})
        for name in ("evaluation/references.json", "budget.json"):
            self.assertEqual(hashlib.sha256((archive/name).read_bytes()).hexdigest(),
                             hashlib.sha256((BASE/name).read_bytes()).hexdigest())

    def test_current_package_contains_no_chinese_text(self):
        for path in BASE.rglob("*"):
            if path.is_file() and path.suffix in (".py", ".json", ".md") and "history" not in path.relative_to(BASE).parts:
                self.assertIsNone(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", path.read_text()), str(path))

    def test_ids_and_claim_numbers_do_not_drive_relation_extraction(self):
        for case in self.cases:
            c, text = self.example(case["case_id"])
            before = predict(c, text)
            c["case_id"], c["group_id"] = "renamed", "unseen-name"
            c["claim_text"] = "Engineering fixture: test the structured claim count only; not a new science case."
            c["declared_counts"] = {"target": 999}
            after = predict(c, text)
            self.assertEqual(before["extraction"], after["extraction"])
            self.assertEqual(after["result"]["label"], "insufficient" if case["case_id"] == "D03" else "inconsistent")

    def test_mix_numerals_and_scope_conditions(self):
        c, text = self.example("D01-S")
        changed = text.replace("three prisms", "four prisms")
        c["declared_counts"] = {"target": 1, "prism": 4, "half_prism": 8}
        p = predict(c, changed)
        self.assertEqual(p["result"]["counts"], {"target": 1, "prism": 4, "half_prism": 8})
        self.assertEqual(p["result"]["label"], "supported")
        c["scope"]["same_curing_scheme"] = False
        self.assertIsNone(predict(c, text)["result"]["label"])

    def test_build_ids_are_extracted_and_scope_filtered(self):
        c, text = self.example("D02")
        text = text.replace("7, 8, and 9", "17, 18, and 19")
        c["scope"]["specimen_ids"] = ["17", "19"]
        p = predict(c, text)
        self.assertEqual(p["extraction"]["relation"]["memberships"], [["17", "build1"], ["19", "build1"]])
        c["scope"]["specimen_ids"] = ["7"]
        self.assertIsNone(predict(c, text)["result"]["label"])

    def test_heat_scope_and_duplicate_ids(self):
        c, text = self.example("H01-L")
        text = text.replace("1, 10, 16, 19, and 24", "2, 4, 4, 6, 8, and 10")
        c["scope"]["column_ids"] = ["2", "4", "6", "8", "10", "10"]
        self.assertEqual(predict(c, text)["result"]["count"], 5)
        c["target_treatment"] = "whole-specimen heat treatment"
        self.assertEqual(predict(c, text)["result"]["count"], 1)
        c["scope"]["temperature_c"] = 800
        self.assertIsNone(predict(c, text)["result"]["label"])

    def test_c02_correct_operator_and_six_row_range(self):
        c, text = self.example("C02-S")
        p = predict(c, text)
        self.assertEqual([r["operator"] for r in p["extraction"]["relation"]["scan_rows"]], ["O1"]*3+["O3"]*3)
        c["scope"]["operators"] = ["O1"]
        p = predict(c, text)
        self.assertEqual((p["result"]["count"], p["result"]["label"]), (1, "inconsistent"))
        c["scope"]["part_ids"].append("1C")
        self.assertIsNone(predict(c, text)["result"]["label"])

    def test_d03_three_fields_and_no_invented_run_count(self):
        c, text = self.example("D03")
        p = predict(c, text)
        self.assertEqual(p["extraction"]["relation"]["atoms"], {"treatment_level": "water_bath_temperature_control", "run_boundary": "not_stated", "specimen_assignment": "not_stated"})
        self.assertIsNone(p["result"]["count"])
        # Synthetic positive-record extension must trigger review, not inherit the
        # old insufficient label. This parser does not yet implement run ledgers.
        p = predict(c, text+" The three prisms belong to runs A, B, and C, each with a separately set temperature.")
        self.assertIsNone(p["result"]["label"])
        self.assertEqual(p["route"], "review_before_model_design")

    def test_unknown_or_missing_clauses_are_not_scientific_insufficiency(self):
        for case in self.cases:
            c, text = self.example(case["case_id"])
            for changed in (text+" Additional run details are available.", text.split(". ", 1)[1]):
                p = predict(c, changed)
                self.assertIsNone(p["result"]["label"])
                self.assertEqual(p["model_calls"], 0)

    def test_candidate_omission_only_gates_simulated_branch(self):
        c, text = self.example("D01-O")
        p = predict(c, text)
        self.assertEqual(p["engineering"]["choice"], "other")
        self.assertIsNone(p["engineering"]["downstream_count"])
        self.assertEqual(p["result"]["count"], 1)
        c["engineering"]["choices"].append({"id": "mixing_batch", "text": "One batch from one mixing operation"})
        self.assertEqual(predict(c, text)["engineering"]["action"], "continue")

    def test_no_reference_or_network_access_during_predictions(self):
        examples = [self.example(c["case_id"]) for c in self.cases]
        with patch("pathlib.Path.open", side_effect=AssertionError("file access")), patch("builtins.open", side_effect=AssertionError("file access")), patch("socket.socket", side_effect=AssertionError("network")):
            for c, text in examples:
                self.assertEqual(predict(c, text)["extraction"]["status"], "parsed")

    def test_input_allowlist_rejects_gold(self):
        validate_inputs(self.cases, self.groups, self.sources)
        cases = deepcopy(self.cases)
        cases[0]["reference_label"] = "inconsistent"
        with self.assertRaises(ValueError):
            validate_inputs(cases, self.groups, self.sources)

    def test_budget_history_and_no_paid_mode(self):
        matrix = make_matrix(self.cases, self.all_predictions(), self.budget)
        self.assertEqual(matrix["initial_remaining_after_worst_case_usd"], "0.331958884")
        self.assertEqual(matrix["worst_batch_cost_usd"], "0.000000000")
        for key, value in (("paid_execution_enabled", True), ("max_retries", 1), ("initial_stage_remaining", "1")):
            b = {**self.budget, key: value}
            with self.assertRaises(ValueError):
                make_matrix(self.cases, self.all_predictions(), b)
        result = subprocess.run([sys.executable, str(BASE/"run.py"), "--mode", "live"], capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_offline_runner_records_nulls_and_empty_attempts(self):
        with tempfile.TemporaryDirectory() as tmp, patch("socket.socket", side_effect=AssertionError("network")):
            out = Path(tmp)/"run"
            self.assertEqual(run(out), 0)
            self.assertEqual((out/"model_attempts.jsonl").read_text(), "")
            summary = json.loads((out/"resource_summary.json").read_text())
            self.assertIsNone(summary["human_cost_usd"])
            self.assertIsNone(summary["model_tokens"])
            self.assertGreater(summary["local_runner_seconds"], 0)
            self.assertIsNone(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", (out/"SUMMARY.md").read_text()))
            self.assertEqual(json.loads((out/"manifest.json").read_text())["language"], "en")
            with self.assertRaises(FileExistsError):
                run(out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
