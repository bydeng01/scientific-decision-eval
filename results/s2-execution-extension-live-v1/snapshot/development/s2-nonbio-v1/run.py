"""Offline S2 entry point. Standard library only; no credentials or network client."""

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import platform
import time

from rules import predict

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def read_json(path):
    return json.loads(path.read_text())


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def jsonl(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_inputs(cases, groups, sources):
    def require(ok):
        if not ok:
            raise ValueError("input contract mismatch")
    require(len({c["case_id"] for c in cases}) == len(cases))
    require(len({g["group_id"] for g in groups}) == len(groups))
    source_ids = {s["source_id"] for s in sources}
    group_ids = {g["group_id"] for g in groups}
    for c in cases:
        require(set(c) <= {"case_id", "group_id", "target_treatment", "scope", "claim_text", "declared_counts", "engineering"})
        require(c["group_id"] in group_ids and bool(c["claim_text"]))
        require(c["declared_counts"] and "target" in c["declared_counts"])
        require(all(type(v) is int and v >= 0 for v in c["declared_counts"].values()))
    for g in groups:
        require(set(g) == {"group_id", "source_id", "source_locations", "evidence_text", "evidence_origin"})
        require(g["source_id"] in source_ids and bool(g["evidence_text"]))


def make_matrix(cases, predictions, budget):
    if budget["paid_execution_enabled"] or any(budget[k] != 0 for k in ("max_model_calls", "max_retries", "max_fallbacks")):
        raise ValueError("This entry point supports only the zero-call preflight")
    history = Decimal(budget["historical_reported_or_estimated_cost"])
    remaining = Decimal(budget["initial_stage_cap"]) - history
    if remaining != Decimal(budget["initial_stage_remaining"]) or remaining < 0:
        raise ValueError("Historical budget does not reconcile")
    if Decimal(budget["total_cap"]) < Decimal(budget["initial_stage_cap"]):
        raise ValueError("Stage cap exceeds total cap")
    rows = []
    for case, p in zip(cases, predictions):
        atoms = (p["extraction"].get("relation") or {}).get("atoms", {})
        rows.append({"case_id": case["case_id"], "group_id": case["group_id"],
                     "variant": case["case_id"], "route": p["route"],
                     "resolved_atomic_fields": list(atoms) if atoms else (["unit_and_membership"] if p["extraction"]["status"] == "parsed" else []),
                     "remaining_atomic_questions": [],
                     "unresolved_input_review": p["extraction"]["failure"],
                     "model": None, "interface": None, "model_repeats": 0,
                     "base_calls": 0, "retry_limit": 0, "fallback_limit": 0,
                     "max_attempts_including_failures": 0, "worst_cost_usd": "0.000000000"})
    return {"language": "en", "input_revision": "s2-nonbio-en-v1", "status": "no_model_branch" if all(p["extraction"]["status"] == "parsed" for p in predictions) else "review_required_no_calls_authorized",
            "rows": rows, "total_max_attempts_including_failures": 0,
            "worst_batch_cost_usd": "0.000000000", "failure_retry_reserve_usd": "0.000000000",
            "initial_remaining_after_worst_case_usd": str(remaining),
            "total_remaining_after_worst_case_usd": str(Decimal(budget["total_cap"]) - history),
            "within_budget": Decimal(0) <= remaining}


def run(output):
    started = datetime.now(timezone.utc).isoformat()
    t0, cpu0 = time.perf_counter(), time.process_time()
    output.mkdir(parents=True, exist_ok=False)
    files = [BASE/"inputs"/f for f in ("cases.json", "evidence.json", "sources.json")]
    cases, group_list, sources = [read_json(f) for f in files]
    validate_inputs(cases, group_list, sources)
    groups = {g["group_id"]: g for g in group_list}
    budget = read_json(BASE/"budget.json")
    events, predictions, actual_inputs = [], [], []
    for case in cases:
        group = groups[case["group_id"]]
        actual = {"case": case, "evidence_text": group["evidence_text"],
                  "source_id": group["source_id"], "source_locations": group["source_locations"]}
        actual_inputs.append(actual)
        begin, cpu = time.perf_counter(), time.process_time()
        prediction = predict(case, group["evidence_text"])
        predictions.append(prediction)
        events.append({"case_id": case["case_id"], "stage": "text_rules_and_deterministic_conclusion",
                       "elapsed_seconds": time.perf_counter()-begin, "cpu_seconds": time.process_time()-cpu,
                       "model_calls": 0, "api_cost_usd": "0", "api_cost_basis": "no requests issued",
                       "input_tokens": None, "output_tokens": None, "reasoning_tokens": None,
                       "cache_tokens": None, "token_status": "not_measured_no_model_request",
                       "api_latency_seconds": None, "api_latency_status": "not_measured",
                       "failure": prediction["extraction"]["failure"]})
    # Persist rule outputs before loading anything in evaluation/.
    jsonl(output/"actual_inputs.jsonl", actual_inputs)
    jsonl(output/"predictions.jsonl", predictions)
    prediction_hash = digest(output/"predictions.jsonl")
    matrix = make_matrix(cases, predictions, budget)
    dump(output/"call_matrix.json", matrix)
    jsonl(output/"model_requests.jsonl", [])
    jsonl(output/"model_attempts.jsonl", [])
    from score import evaluate
    scoring_start = time.perf_counter()
    refs_file = BASE/"evaluation/references.json"
    scores, oracle = evaluate(predictions, cases, read_json(refs_file))
    scores["summary"].update({"groups": len(groups), "sources": len(sources),
                              "language": "en", "input_revision": "s2-nonbio-en-v1",
                              "source_groups": {s["source_id"]: [g["group_id"] for g in group_list if g["source_id"] == s["source_id"]] for s in sources}})
    dump(output/"scores.json", scores)
    jsonl(output/"oracle_predictions.jsonl", oracle)
    events.append({"stage": "scoring_and_human_oracle_diagnostic", "elapsed_seconds": time.perf_counter()-scoring_start,
                   "model_calls": 0, "failure": None})
    jsonl(output/"resources.jsonl", events)
    all_checks = all(all(r[k] for k in ("relation_exact", "count_correct", "label_correct", "action_correct", "oracle_count_correct", "oracle_label_correct")) and r.get("engineering_correct", True) for r in scores["per_case"])
    manifest_files = files + [refs_file, BASE/"budget.json", BASE/"run.py", BASE/"rules.py", BASE/"score.py", BASE/"test_preflight.py", BASE/"check_counts.py", BASE/"official_api_check.json", BASE/"text_revision.json"]
    def fraction(lane, key):
        value = scores["summary"][lane][key]
        return f"{value['correct']}/{value['denominator']}"
    scientific_n = scores["summary"]["scientific_items"]
    engineering_n = scores["summary"]["engineering_items"]
    lines = ["# S2 non-biological development preflight: English results", "",
             f"{len(groups)} groups, {len(cases)} items, {len(sources)} sources; {scientific_n} scientific claims and {engineering_n} engineering routing check. Reviewed development data.", "",
             "Input revision: s2-nonbio-en-v1. These results come from a fresh run on the English passages. Earlier Chinese runs remain historical.", "",
             "| Item | Route | Count | Label | New model calls |", "|---|---|---:|---|---:|"]
    for c, p in zip(cases, predictions):
        n = p["result"]["count"]
        label = p["result"]["label"] or "unresolved"
        lines.append(f"| {c['case_id']} | {p['route']} | {n if n is not None else 'unknown'} | {label} | 0 |")
    lines += ["", "D01-O's table entry is the normal rule result. Its separate candidate-omission simulation returns other, stops downstream counting in that branch, and requests candidate completion or transfer.", "",
              "Text rules: " + ", ".join(f"{name} {fraction('text_rules', key)}" for name, key in (("relation", "relation_exact"), ("count", "count_correct"), ("label", "label_correct"), ("action", "action_correct"))) + ".",
              f"Human relation oracle: count {fraction('human_oracle', 'oracle_count_correct')}, label {fraction('human_oracle', 'oracle_label_correct')}. See scores.json for item-level results.",
              "D03 scores treatment level, run boundary and specimen assignment separately. The latter two are not stated; the run count remains unknown.",
              "", f"Offline scoring checks passed: {all_checks}. Call-matrix status: {matrix['status']}.",
              "Model-call, retry and fallback limits are all zero. Worst-case new API cost is $0; historical reported/estimated cost is $0.668041116.",
              "", "Evaluation uses a finite phrase grammar on manually prepared English passages with supplied targets, scopes and claim numbers. Unseen-source performance, arbitrary-paper/PDF extraction and model quality are unmeasured.",
              "Source localization, transcription, translation/review, rule development and later record requests are outside the measured execution interval. Human time, local compute costs, tokens, API latency and full-workflow time remain unmeasured; missing values stay null.",
              "resource_summary.json records local execution timing."]
    (output/"SUMMARY.md").write_text("\n".join(lines)+"\n")
    dump(output/"resource_summary.json", {"started_at_utc": started,
        "local_runner_seconds": time.perf_counter()-t0, "local_runner_cpu_seconds": time.process_time()-cpu0,
        "timing_boundary": "run() entry through summary generation; excludes final resource-summary/manifest writes, interpreter startup, tests, documentation, source preparation and record follow-up",
        "api_attempts": 0, "api_failures": 0, "api_failure_rate": None,
        "api_failure_rate_status": "not_measured_no_attempts", "new_api_cost_usd": "0.000000000",
        "historical_reported_or_estimated_cost_usd": budget["historical_reported_or_estimated_cost"],
        "initial_stage_remaining_usd": matrix["initial_remaining_after_worst_case_usd"],
        "local_processing_failures": sum(p["extraction"]["failure"] is not None for p in predictions),
        "preparation_time_seconds": None, "human_review_time_seconds": None, "rule_development_time_seconds": None, "translation_review_time_seconds": None,
        "human_cost_usd": None, "local_compute_cost_usd": None, "full_workflow_seconds": None,
        "development_tool_tokens": None, "development_tool_cost_usd": None,
        "unmeasured_status": "not_measured; human work and local compute are not free",
        "model_quality": None, "model_tokens": None, "model_latency_seconds": None,
        "offline_scoring_checks_pass": all_checks})
    dump(output/"manifest.json", {"started_at_utc": started, "python": platform.python_version(),
        "mode": "offline_dry_run", "language": "en", "input_revision": "s2-nonbio-en-v1", "split": "reviewed_development", "paid_execution_enabled": False,
        "input_and_code_sha256": {str(p.relative_to(ROOT)): digest(p) for p in manifest_files},
        "predictions_sha256_before_loading_references": prediction_hash,
        "artifact_sha256": {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()}})
    print(json.dumps({"output": str(output), "checks_pass": all_checks, "model_calls": 0,
                      "matrix_status": matrix["status"], "initial_balance_usd": str(matrix["initial_remaining_after_worst_case_usd"])}, ensure_ascii=False))
    return 0 if all_checks and matrix["status"] == "no_model_branch" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["dry-run"], default="dry-run")
    parser.add_argument("--output", type=Path, default=ROOT/"results"/("s2-nonbio-preflight-en-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")))
    args = parser.parse_args()
    raise SystemExit(run(args.output.resolve()))
