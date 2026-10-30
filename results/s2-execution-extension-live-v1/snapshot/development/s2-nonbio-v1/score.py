"""Evaluation only. Load references after text predictions have been persisted."""

from rules import candidate_check, conclude


def evaluate(predictions, cases, references):
    by_id = {p["case_id"]: p for p in predictions}
    assert len(by_id) == len(predictions) == len(cases) == len(references)
    assert set(by_id) == set(references) == {c["case_id"] for c in cases}
    detail, oracle = [], []
    for case in cases:
        cid = case["case_id"]
        p, ref = by_id[cid], references[cid]
        oracle_extraction = {"status": "parsed", "relation": ref["oracle_relation"]}
        oracle_result = conclude(oracle_extraction, case["declared_counts"])
        oracle.append({"case_id": cid, "result": oracle_result,
                       "origin": "human relation oracle; not text extraction"})
        row = {"case_id": cid, "group_id": case["group_id"],
               "scientific": "engineering" not in case,
               "relation_exact": p["extraction"]["relation"] == ref["oracle_relation"],
               "count_correct": p["result"]["count"] == ref["count"],
               "label_correct": p["result"]["label"] == ref["label"],
               "action_correct": p["result"]["action"] == ref["action"],
               "oracle_count_correct": oracle_result["count"] == ref["count"],
               "oracle_label_correct": oracle_result["label"] == ref["label"],
               "reference_label": ref["label"], "predicted_label": p["result"]["label"],
               "parsed": p["extraction"]["status"] == "parsed"}
        if "engineering" in case:
            row["engineering_correct"] = p["engineering"] == ref["engineering"]
            row["oracle_engineering_correct"] = candidate_check(oracle_extraction, case["engineering"]["choices"]) == ref["engineering"]
        if ref["oracle_relation"]["atoms"]:
            atoms = (p["extraction"].get("relation") or {}).get("atoms", {})
            row["atom_scores"] = {k: atoms.get(k) == v for k, v in ref["oracle_relation"]["atoms"].items()}
        detail.append(row)
    scientific = [r for r in detail if r["scientific"]]
    def tally(key):
        return {"correct": sum(r[key] for r in scientific), "denominator": len(scientific)}
    labels = ["supported", "inconsistent", "insufficient", None]
    confusion = [{"reference": a, "prediction": b,
                  "n": sum(r["reference_label"] == a and r["predicted_label"] == b for r in scientific)}
                 for a in labels[:-1] for b in labels]
    summary = {"split": "reviewed_development", "scientific_items": len(scientific),
               "engineering_items": len(detail)-len(scientific),
               "text_rules": {k: tally(k) for k in ("relation_exact", "count_correct", "label_correct", "action_correct")},
               "human_oracle": {k: tally(k) for k in ("oracle_count_correct", "oracle_label_correct")},
               "confusion_matrix": confusion,
               "incorrect_count_claim_missed": sum(r["reference_label"] == "inconsistent" and r["predicted_label"] != "inconsistent" for r in scientific),
               "incorrect_count_claim_false_alarm": sum(r["reference_label"] != "inconsistent" and r["predicted_label"] == "inconsistent" for r in scientific),
               "model_quality": None, "model_quality_status": "not_measured",
               "post_record_request_quality": None, "post_record_request_quality_status": "not_measured"}
    return {"summary": summary, "per_case": detail}, oracle
