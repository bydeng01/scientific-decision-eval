"""Audit saved S2 responses and produce an analysis sidecar, with sockets disabled."""
from collections import Counter
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import socket
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = ROOT / "results/s2-execution-live-v1"
REPORT = RUN / "reports/20260921T063548757325Z.json"


def no_network(*args, **kwargs):
    raise RuntimeError("This analysis only reads saved responses; network is disabled")


socket.socket = no_network
socket.create_connection = no_network
sys.path.insert(0, str(ROOT / "development/s2-execution-v1"))
import run
from scoring import expected_projection, fraction, projection, score_lane


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def null_paths(value, prefix=()):
    if value is None:
        yield prefix
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from null_paths(child, prefix + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from null_paths(child, prefix + (index,))


def at(value, path):
    for key in path:
        value = value[key]
    return value


def main():
    manifest = run.verify(RUN)
    records = run.validate_attempts(RUN)
    report = read(REPORT)
    config = read(RUN / "config.json")
    groups = read(RUN / "inputs.json")
    refs = read(RUN / "evaluation_only/references.json")
    code = read(RUN / "code_predictions.json")
    actual_artifacts = {
        str(p.relative_to(RUN)): sha(p)
        for p in sorted((RUN / "attempts").rglob("*.json"))
    }
    assert actual_artifacts == report["attempt_artifact_sha256"]
    assert manifest["mode"] == "live"
    assert len(records) == report["planned_requests"] == 300
    assert all(row["simulated"] is False for row in records)
    model_groups = {g["group_id"] for g in groups if g["route"] == "model"}
    by_group = {g["group_id"]: g for g in groups}
    receipts = [read(p) for p in (RUN / "attempts").glob("*/receipt.json")]
    errors, models, preserved_nulls = [], {}, 0
    for model in config["models"]:
        mid = model["id"]
        rows = [row for row in records if row["model_id"] == mid]
        lane = {(rep, row["group_id"]): row
                for rep in range(config["repetitions"]) for row in code}
        lane.update({(row["repeat"], row["group_id"]): row for row in rows})
        rescored = score_lane(groups, refs, lane, config["repetitions"])
        saved = report["model_scores"][mid]
        assert rescored == {k: v for k, v in saved.items() if k != "execution_completion"}
        semantic = [r for r in saved["per_choice"] if r["route"] == "model"]
        observed = [r for r in semantic if r["prediction"] is not None]
        claims = [r for r in saved["per_claim"] if r["group_id"] in model_groups]
        reviewed = [r for r in semantic if r["recent_independent_review"]]
        errors.extend(dict(model_id=mid, repeat_number=r["repeat"] + 1,
                           **{k: v for k, v in r.items() if k != "repeat"})
                      for r in semantic if not r["correct"])
        costs, cache_writes, reasoning = [], [], []
        price = {k: Decimal(str(v)) for k, v in model["usd_per_million"].items()}
        for row in rows:
            usage = row["resources"]["raw_usage"]
            if not usage:
                continue
            inp, out = usage["input_tokens"], usage["output_tokens"]
            if model["provider"] == "openai":
                details = usage["input_tokens_details"]
                cached, written = details["cached_tokens"], details["cache_write_tokens"]
                assert all(type(v) is int and v >= 0 for v in (inp, out, cached, written))
                assert cached + written <= inp
                cost = ((inp - cached - written) * price["input"]
                        + cached * price["cached_input"] + written * price["cache_write"]
                        + out * price["output"]) / Decimal(1000000)
                cache_writes.append(written)
                reasoning.append(usage["output_tokens_details"]["reasoning_tokens"])
            elif model["provider"] == "anthropic":
                cost = (inp * price["input"]
                        + usage["cache_read_input_tokens"] * price["cached_input"]
                        + usage["cache_creation_input_tokens"] * price["cache_write"]
                        + out * price["output"]) / Decimal(1000000)
                cache_writes.append(usage["cache_creation_input_tokens"])
                reasoning.append(usage["output_tokens_details"]["thinking_tokens"])
            else:
                cost = Decimal(str(usage["cost"]))
            costs.append(cost)
            group = by_group[row["group_id"]]
            actual, expected = projection(group, row["derived"]), expected_projection(group, refs)
            for path in null_paths(expected):
                assert at(actual, path) is None, (mid, row["job_id"], path)
                preserved_nulls += 1
        subtotal = float(sum(costs))
        resource = report["resources_by_model"][mid]
        models[mid] = {
            "served_models": resource["served_models"],
            "planned_requests": 50,
            "valid_responses": sum(r["status"] == "complete" for r in rows),
            "semantic_choices_fixed_denominator": saved["model_routed_semantic_choices"],
            "semantic_choices_observed_only_secondary": fraction(sum(r["correct"] for r in observed), len(observed)),
            "model_dependent_outcomes_exact": fraction(sum(r["exact"] for r in claims), len(claims)),
            "model_dependent_labels_exact": fraction(sum(r["label_exact"] for r in claims), len(claims)),
            "reviewed_subset_model_choices": fraction(sum(r["correct"] for r in reviewed), len(reviewed)),
            "full_scientific_workflow_choices": saved["scientific_workflow_choices"],
            "per_repeat": saved["per_repeat"],
            "variable_question_ids": sorted(q for q, s in saved["stability"].items() if len(s["distinct_valid_answers"]) > 1),
            "latency_seconds": resource["latency_summary_seconds"],
            "latency_known_requests": len(costs),
            "input_tokens": resource["input_tokens"],
            "output_tokens": resource["output_tokens"],
            "cache_write_tokens_reconciled_known_subtotal": sum(cache_writes) if cache_writes else None,
            "reasoning_or_thinking_tokens_reconciled_known_subtotal": sum(reasoning) if reasoning else None,
            "cost": {
                "basis": "provider_reported" if mid == "jev" else "saved_usage_and_run_price_snapshot_estimate",
                "known_subtotal_usd": subtotal,
                "total_usd": subtotal if len(costs) == len(rows) else None,
                "missing_requests": len(rows) - len(costs),
                "provider_reported_original": resource["reported_cost_usd"],
                "original_upper_estimate": resource["usage_cost_upper_estimate_usd"],
            },
        }
    reference_fallbacks = Counter(refs["answers"][q["question_id"]]
                                  for g in groups if g["route"] == "model" for q in g["questions"]
                                  if refs["answers"][q["question_id"]] in {"other", "not_stated", "conflicting"})
    output = {
        "source_report": str(REPORT.relative_to(ROOT)),
        "source_report_sha256": sha(REPORT),
        "analysis_script_sha256": sha(Path(__file__)),
        "scope": {"groups": len(groups), "scientific_choices": 40, "engineering_choices": 1,
                  "code_scientific_choices": 20, "model_scientific_choices": 20,
                  "model_groups": len(model_groups), "models": len(models), "repeats": 5,
                  "independently_reviewed_choices": 18, "independently_reviewed_model_choices": 14},
        "execution": {"terminal_records": len(records), "http_200": sum(r["http_status"] == 200 for r in receipts),
                      "uncertain_transport": sum(r.get("transport_error") == "InterruptedWithoutReceipt" for r in receipts),
                      "retries": report["retries"], "fallbacks": report["fallbacks"],
                      "manifest_to_report_seconds": (datetime.fromisoformat(report["created_at"]) - datetime.fromisoformat(manifest["created_at"])).total_seconds()},
        "verification": {"prepared_source_and_request_hashes": "passed", "saved_response_reparse": "passed",
                         "attempt_artifacts_matching_original_report": len(actual_artifacts),
                         "rescored_model_reports_exactly_equal": len(models),
                         "expected_null_fields_preserved_in_received_model_derivations": preserved_nulls,
                         "network": "disabled", "new_model_calls": 0},
        "models": models,
        "errors": errors,
        "code_only": {"scientific_choices": report["code_only"]["scientific_workflow_choices"],
                      "scientific_outcomes": report["code_only"]["scientific_claims"]["exact"]},
        "oracle": report["oracle"],
        "model_reference_fallback_counts": dict(reference_fallbacks),
        "reconciled_cost": {"known_response_subtotal_usd": float(sum(Decimal(str(m["cost"]["known_subtotal_usd"])) for m in models.values())),
                            "total_usd": None, "unknown_requests": ["r01-B002-terra"],
                            "basis": "Jev reported cost plus other providers' token-price estimates; not an invoice"},
        "accounting_findings": [
            {"location": "development/s2-execution-v1/providers.py:118", "field": "input_tokens_details.cache_write_tokens",
             "impact": "199 OpenAI responses have this field; old normalization reads cache_creation_tokens instead. Quality scores unaffected. Reconciled only in this analysis."},
            {"location": "development/s2-execution-v1/providers.py:120", "field": "output_tokens_details.thinking_tokens",
             "impact": "50 Anthropic responses have this field; old normalization reads reasoning_tokens instead. Output totals and cost already include these tokens."},
        ],
    }
    data = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    path = HERE / "summary.json"
    if path.exists():
        assert path.read_text() == data, "Existing analysis differs; use a new analysis directory"
    else:
        with path.open("x") as stream:
            stream.write(data)
    print(json.dumps({"output": str(path.relative_to(ROOT)), "verification": output["verification"],
                      "reconciled_cost": output["reconciled_cost"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
