"""Reparse and audit both saved S2 cohorts. No network or credential access."""
import argparse
from collections import Counter
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import socket
import statistics
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COHORTS = {
    "original": ("s2-execution-v1", "s2-execution-live-v1"),
    "extension": ("s2-execution-v2", "s2-execution-extension-live-v1"),
}


def blocked(*args, **kwargs):
    raise RuntimeError("Offline analysis: model execution and networking are disabled")


socket.socket = socket.create_connection = blocked
sys.dont_write_bytecode = True


def audit_hook(event, args):
    if event.startswith("socket."):
        blocked()
    if event == "open" and isinstance(args[0], (str, bytes)):
        name = Path(args[0].decode() if isinstance(args[0], bytes) else args[0]).name
        if name.startswith(".env"):
            raise RuntimeError("Credential files are outside this analysis")


sys.addaudithook(audit_hook)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(name, value):
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path = HERE / name
    if path.exists():
        assert path.read_text() == text, f"Changed analysis: use a new directory ({name})"
    else:
        with path.open("x") as stream:
            stream.write(text)


def fraction(correct, n):
    return {"correct": correct, "denominator": n, "accuracy": correct / n if n else None}


def aggregate(values):
    known = [v for v in values if v is not None]
    subtotal = sum(known) if known else None
    return {"known_subtotal": subtotal, "known_records": len(known),
            "missing_records": len(values) - len(known),
            "total": subtotal if len(known) == len(values) else None}


def latency(values):
    known = sorted(v for v in values if v is not None)
    return {"known_records": len(known), "missing_records": len(values) - len(known),
            "sum": sum(known), "median": statistics.median(known) if known else None,
            "p95_nearest_rank": known[math.ceil(.95 * len(known)) - 1] if known else None}


def null_paths(value, prefix=()):
    if value is None:
        yield prefix
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from null_paths(v, prefix + (k,))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from null_paths(v, prefix + (i,))


def at(value, path):
    for part in path:
        value = value[part]
    return value


def resources(model, receipt):
    """Read raw usage, preserving absent fields; reasoning is part of output."""
    obj = json.loads(receipt["raw_body"]) if receipt["raw_body"] else {}
    u = obj.get("usage") or {}
    chat = model["provider"] == "openrouter_chat"
    inp = u.get("prompt_tokens" if chat else "input_tokens")
    out = u.get("completion_tokens" if chat else "output_tokens")
    d = u.get("prompt_tokens_details" if chat else "input_tokens_details") or {}
    od = u.get("completion_tokens_details" if chat else "output_tokens_details") or {}
    cached = u.get("cache_read_input_tokens", d.get("cached_tokens"))
    written = u.get("cache_creation_input_tokens", d.get("cache_write_tokens", d.get("cache_creation_tokens")))
    thinking = od.get("reasoning_tokens", od.get("thinking_tokens"))
    for v in (inp, out, cached, written, thinking):
        assert v is None or (type(v) is int and v >= 0)
    assert thinking is None or (out is not None and thinking <= out)
    price = {k: Decimal(str(v)) for k, v in model["usd_per_million"].items()}
    estimate = None
    if inp is not None and out is not None:
        if model["provider"] == "openrouter":
            estimate = inp * price["input"] + out * price["output"]
        elif cached is not None and written is not None:
            if model["provider"] == "anthropic":
                ordinary = inp
            else:
                assert cached + written <= inp
                ordinary = inp - cached - written
            assert written == 0 or "cache_write" in price
            estimate = (ordinary * price["input"] + cached * price["cached_input"]
                        + written * price.get("cache_write", Decimal(0)) + out * price["output"])
    estimate = float(estimate / Decimal(1000000)) if estimate is not None else None
    reported = u.get("cost")
    assert reported is None or (type(reported) in (int, float) and math.isfinite(reported) and reported >= 0)
    metadata = (obj.get("error") or {}).get("metadata") or {}
    return {"input_tokens": inp, "output_tokens": out, "cached_input_tokens": cached,
            "cache_write_tokens": written, "reasoning_or_thinking_tokens": thinking,
            "reported_cost_usd": reported, "usage_estimate_usd": estimate,
            "selected_cost_usd": reported if reported is not None else estimate,
            "selected_cost_basis": "server_reported" if reported is not None else
                "saved_usage_price_estimate" if estimate is not None else "unknown",
            "latency_seconds": receipt["latency_seconds"],
            "error_provider": metadata.get("provider_name"),
            "limit_source": metadata.get("limit_source")}


def analyze_cohort(name):
    package, directory = COHORTS[name]
    sys.path.insert(0, str(ROOT / "development" / package))
    import run
    import providers
    from scoring import score_lane, projection, expected_projection, oracle, load_references
    run.execute = run.http_transport = providers.http_transport = blocked
    path = ROOT / "results" / directory
    before = {str(p.relative_to(ROOT)): sha(p) for p in path.rglob("*") if p.is_file()}
    manifest = run.verify(path)
    records = run.validate_attempts(path)
    config, groups, plan = (read(path / f"{x}.json") for x in ("config", "inputs", "plan"))
    refs = read(path / "evaluation_only/references.json")
    code = read(path / "code_predictions.json")
    assert refs == load_references(groups)
    assert groups == run.load_inputs()
    assert manifest["config_sha256"] == run.digest(config)
    regenerated = run.run_code(groups)
    for saved, actual in zip(code, regenerated, strict=True):
        assert {k: v for k, v in saved.items() if k not in {"wall_seconds", "cpu_seconds"}} == {
            k: v for k, v in actual.items() if k not in {"wall_seconds", "cpu_seconds"}}
    oracle_result = oracle(groups, refs)
    old_oracle = read(path / "evaluation_only/oracle.json")
    assert oracle_result == {k: v for k, v in old_oracle.items() if k != "wall_seconds"}
    assert manifest["mode"] == "live" and all(not r["simulated"] for r in records)
    reports = sorted((path / "reports").glob("*.json"))
    report_path = reports[-1]
    report = read(report_path)
    artifact_hashes = {str(p.relative_to(path)): sha(p) for p in sorted((path / "attempts").rglob("*.json"))}
    assert artifact_hashes == report["attempt_artifact_sha256"]
    jobs = {j["job_id"]: j for j in plan["jobs"]}
    by_group = {g["group_id"]: g for g in groups}
    by_record = {r["job_id"]: r for r in records}
    assert len(by_record) == len(records)
    model_groups = {g["group_id"] for g in groups if g["route"] == "model"}
    requests, choices, outcomes, models, rescored = [], [], [], {}, {}
    intents, receipts = {}, {}
    for jid, job in jobs.items():
        d = path / "attempts" / jid
        if (d / "intent.json").exists():
            intents[jid] = read(d / "intent.json")
            assert intents[jid]["attempt"] == 1
            assert intents[jid]["request_sha256"] == run.digest(intents[jid]["request"]) == job["request_sha256"]
        if (d / "receipt.json").exists():
            receipts[jid] = read(d / "receipt.json")
    pending = sorted(set(intents) - set(receipts))
    unfinished = sorted(set(jobs) - set(by_record))
    assert not unfinished, "This completed-cohort analysis requires a new snapshot if a cohort is incomplete"
    preserved_nulls = 0
    for model in config["models"]:
        mid = model["id"]
        rows = [r for r in records if r["model_id"] == mid]
        lane = {(rep, r["group_id"]): r for rep in range(config["repetitions"]) for r in code}
        lane.update({(r["repeat"], r["group_id"]): r for r in rows})
        scored = score_lane(groups, refs, lane, config["repetitions"])
        assert scored == {k: v for k, v in report["model_scores"][mid].items() if k != "execution_completion"}
        rescored[mid] = scored
        sc = [r for r in scored["per_choice"] if r["route"] == "model"]
        oc = [r for r in scored["per_claim"] if r["group_id"] in model_groups]
        detail_rows = []
        for row in rows:
            jid = row["job_id"]
            rc = receipts[jid]
            res = resources(model, rc)
            if res["reported_cost_usd"] is not None and res["usage_estimate_usd"] is not None:
                assert abs(res["reported_cost_usd"] - res["usage_estimate_usd"]) < 1e-10
            # V1 omissions are reconciled from raw usage; other stored fields must agree.
            for key, old_key in [("input_tokens", "input_tokens"), ("output_tokens", "output_tokens"),
                                 ("cached_input_tokens", "cached_input_tokens"), ("reported_cost_usd", "reported_cost_usd")]:
                assert res[key] == row["resources"][old_key]
            if name == "extension":
                assert res["cache_write_tokens"] == row["resources"]["cache_creation_tokens"]
                assert res["reasoning_or_thinking_tokens"] == row["resources"]["reasoning_tokens"]
                saved_cost = row["resources"]["usage_cost_estimate_usd"]
                assert (saved_cost is None and res["usage_estimate_usd"] is None) or abs(saved_cost - res["usage_estimate_usd"]) < 1e-10
            req = {"cohort": name, "model_id": mid, "job_id": jid, "repeat_number": row["repeat"] + 1,
                   "group_id": row["group_id"], "status": row["status"], "http_status": rc["http_status"],
                   "transport_error": rc["transport_error"], "errors": row["errors"],
                   "started_at": intents[jid]["started_at"], "received_at": rc.get("received_at"),
                   "served_model": row["served_model"], "served_provider": row.get("served_provider"),
                   "receipt_path": str((path / "attempts" / jid / "receipt.json").relative_to(ROOT)),
                   "request_sha256": row["request_sha256"], "receipt_canonical_sha256": row["receipt_sha256"],
                   "raw_body_sha256": hashlib.sha256(rc["raw_body"].encode()).hexdigest() if rc["raw_body"] is not None else None, **res}
            requests.append(req)
            detail_rows.append(req)
            group = by_group[row["group_id"]]
            actual, expected = projection(group, row["derived"]), expected_projection(group, refs)
            claim = next(x for x in oc if x["group_id"] == row["group_id"] and x["repeat"] == row["repeat"])
            assert claim["exact"] == (actual == expected)
            label_key = "claim_assessment" if group["package"] == "nonbio" else "final_label"
            assert claim["label_exact"] == (actual is not None and actual[label_key] == expected[label_key])
            outcomes.append({"cohort": name, "model_id": mid, "job_id": jid,
                             **claim, "actual": actual, "reference": expected})
            if actual is not None:
                for np in null_paths(expected):
                    assert at(actual, np) is None, (jid, np)
                    preserved_nulls += 1
        for choice in sc:
            row = lane[(choice["repeat"], choice["group_id"])]
            assert choice["correct"] == (row["answers"].get(choice["question_id"]) == refs["answers"][choice["question_id"]])
            failure = choice["failure"]
            category = ("correct" if choice["correct"] else "semantic_error" if choice["prediction"] is not None
                        else "transport_uncertain" if failure == "transport_uncertain"
                        else "http_failure" if failure and failure.startswith("http_")
                        else "missing_answer" if failure in {"missing_answer", "not_attempted"}
                        else "format_or_contract_error")
            choices.append({"cohort": name, "model_id": mid, "job_id": row["job_id"],
                            **choice, "category": category})
        selected = [r["selected_cost_usd"] for r in detail_rows]
        cost = aggregate(selected)
        successful = [r for r in detail_rows if r["status"] == "complete"]
        observed = [x for x in sc if x["prediction"] is not None]
        reviewed = [x for x in sc if x["recent_independent_review"]]
        stability = {}
        for qid in sorted({x["question_id"] for x in sc}):
            qrows = [x for x in sc if x["question_id"] == qid]
            vals = [x["prediction"] for x in qrows if x["prediction"] is not None]
            stability[qid] = {"reference": refs["answers"][qid], "answers_in_repeat_order": [x["prediction"] for x in qrows],
                              "failure_in_repeat_order": [x["failure"] for x in qrows],
                              "valid_answer_counts": dict(Counter(vals)), "missing": 5 - len(vals),
                              "all_five_correct": all(x["correct"] for x in qrows),
                              "all_five_same_valid_answer": len(vals) == 5 and len(set(vals)) == 1,
                              "multiple_valid_answers": len(set(vals)) > 1}
        per_repeat = []
        for rep in range(5):
            rs = [r for r in detail_rows if r["repeat_number"] == rep + 1]
            cs = [r for r in sc if r["repeat"] == rep]
            os = [r for r in oc if r["repeat"] == rep]
            valid = [r for r in cs if r["prediction"] is not None]
            per_repeat.append({"repeat_number": rep + 1, "semantic_fixed": fraction(sum(x["correct"] for x in cs), len(cs)),
                               "semantic_observed": fraction(sum(x["correct"] for x in valid), len(valid)),
                               "outcomes_exact": fraction(sum(x["exact"] for x in os), len(os)),
                               "labels_exact": fraction(sum(x["label_exact"] for x in os), len(os)),
                               "failed_requests": sum(x["status"] != "complete" for x in rs),
                               "successful_latency": latency([x["latency_seconds"] for x in rs if x["status"] == "complete"]),
                               "cost": aggregate([x["selected_cost_usd"] for x in rs])})
        models[mid] = {"cohort": name, "configuration": model, "planned_requests": 50,
                       "successful_requests": len(successful), "failed_requests": 50 - len(successful),
                       "served_models": sorted({r["served_model"] for r in rows if r["served_model"]}),
                       "served_providers": sorted({r["served_provider"] for r in detail_rows if r["served_provider"]}),
                       "semantic_fixed": fraction(sum(x["correct"] for x in sc), len(sc)),
                       "semantic_observed_secondary": fraction(sum(x["correct"] for x in observed), len(observed)),
                       "model_dependent_outcomes_exact": fraction(sum(x["exact"] for x in oc), len(oc)),
                       "model_dependent_counts_exact": fraction(sum(x["counts_exact"] for x in oc), len(oc)),
                       "model_dependent_labels_exact": fraction(sum(x["label_exact"] for x in oc), len(oc)),
                       "reviewed_model_subset": fraction(sum(x["correct"] for x in reviewed), len(reviewed)),
                       "choice_categories": dict(Counter(x["category"] for x in choices if x["model_id"] == mid)),
                       "per_repeat": per_repeat, "stability": stability,
                       "all_five_correct_questions": sum(x["all_five_correct"] for x in stability.values()),
                       "variable_questions": [q for q, x in stability.items() if x["multiple_valid_answers"]],
                       "latency_all_terminal": latency([x["latency_seconds"] for x in detail_rows]),
                       "latency_successful": latency([x["latency_seconds"] for x in successful]),
                       "latency_failed": latency([x["latency_seconds"] for x in detail_rows if x["status"] != "complete"]),
                       "resources": {key: aggregate([x[key] for x in detail_rows]) for key in (
                           "input_tokens", "output_tokens", "cached_input_tokens", "cache_write_tokens", "reasoning_or_thinking_tokens")},
                       "cost": {"server_reported": aggregate([x["reported_cost_usd"] for x in detail_rows]),
                                "usage_estimate": aggregate([x["usage_estimate_usd"] for x in detail_rows]),
                                "selected_reported_else_estimated": cost,
                                "selected_basis_counts": dict(Counter(x["selected_cost_basis"] for x in detail_rows)),
                                "unknown_job_ids": [x["job_id"] for x in detail_rows if x["selected_cost_usd"] is None],
                                "known_cost_per_successful_request": sum(x["selected_cost_usd"] for x in successful) / len(successful),
                                "billed_invoice_total_usd": None}}
        assert models[mid]["semantic_fixed"] == scored["model_routed_semantic_choices"]
    after = {str(p.relative_to(ROOT)): sha(p) for p in path.rglob("*") if p.is_file()}
    assert before == after, "Source run changed while being read"
    sources = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / "development" / package).glob("*") if p.is_file()}
    out = {"cohort": name, "models": models, "requests": requests, "choices": choices, "outcomes": outcomes,
           "execution": {"planned": plan["requests"], "intents": len(intents), "receipts": len(receipts),
                         "predictions": len(records), "http_status_counts": dict(Counter(str(x["http_status"]) for x in receipts.values())),
                         "pending_intents": pending, "unfinished_jobs": unfinished,
                         "not_started": sorted(set(jobs) - set(intents)), "retries": 0, "fallbacks": 0,
                         "first_intent_at": min(x["started_at"] for x in intents.values()),
                         "last_receipt_at": max(x.get("received_at") or "" for x in receipts.values()),
                         "source_report_created_at": report["created_at"]},
           "verification": {"source_files": len(manifest["source_sha256"]), "prepared_artifacts": len(manifest["artifact_sha256"]),
                            "attempt_artifacts": len(artifact_hashes), "reparsed_predictions": len(records),
                            "score_objects_equal": len(models), "null_fields_preserved": preserved_nulls,
                            "source_report": str(report_path.relative_to(ROOT)), "source_report_sha256": sha(report_path),
                            "git_head": manifest["git_head"], "git_status": manifest["git_status"],
                            "prepared_inputs_equal_current_loader": True, "saved_references_equal_current_loader": True,
                            "code_outputs_rederived": len(code), "oracle_groups_exact": oracle_result["groups_correct"],
                            "all_original_run_files_unchanged": True},
           "protected_sha256": {**before, **{k: sha(ROOT / k) for k in manifest["source_sha256"]}, **sources},
           "code_only": {"scientific_choices": report["code_only"]["scientific_workflow_choices"],
                         "scientific_outcomes": report["code_only"]["scientific_claims"]["exact"]},
           "model_reference_options": dict(Counter(refs["answers"][q["question_id"]] for g in groups if g["route"] == "model" for q in g["questions"])),
           "model_reference_labels": {g["group_id"]: expected_projection(g, refs).get("claim_assessment", expected_projection(g, refs).get("final_label"))
                                      for g in groups if g["route"] == "model"}}
    emit(f"audit-{name}.json", out)
    emit(f"rescored-{name}.json", rescored)
    print(json.dumps({"cohort": name, "verification": out["verification"], "execution": out["execution"]}))


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--cohort", choices=COHORTS)
    selected = args.parse_args().cohort
    if selected:
        analyze_cohort(selected)
        return
    # Separate interpreters bind each cohort to its own parser and normalizer.
    for name in COHORTS:
        subprocess.run([sys.executable, "-B", str(Path(__file__)), "--cohort", name], cwd=ROOT, check=True)
    audits = {name: read(HERE / f"audit-{name}.json") for name in COHORTS}
    paths = [ROOT / "results" / d for _, d in COHORTS.values()]
    for filename in ("inputs.json", "evaluation_only/references.json"):
        assert paths[0].joinpath(filename).read_bytes() == paths[1].joinpath(filename).read_bytes()
    for filename in ("dataset.py", "derive.py", "scoring.py"):
        assert (ROOT / "development/s2-execution-v1" / filename).read_bytes() == (ROOT / "development/s2-execution-v2" / filename).read_bytes()
    plans = [read(p / "plan.json") for p in paths]
    packets = [{j["group_id"]: (j["packet"], j["question_map"]) for j in p["jobs"]} for p in plans]
    assert packets[0] == packets[1]
    previous = read(ROOT / "results/s2-execution-analysis-v1/summary.json")
    models = {mid: m for a in audits.values() for mid, m in a["models"].items()}
    for mid, old in previous["models"].items():
        new = models[mid]
        assert old["semantic_choices_fixed_denominator"] == new["semantic_fixed"]
        assert old["model_dependent_outcomes_exact"] == new["model_dependent_outcomes_exact"]
        assert old["model_dependent_labels_exact"] == new["model_dependent_labels_exact"]
        assert abs(old["cost"]["known_subtotal_usd"] - new["cost"]["selected_reported_else_estimated"]["known_subtotal"]) < 1e-12
    baseline = read(ROOT / "results/s2-execution-extension-preexisting-sha256.json")
    assert all(sha(ROOT / p) == h for p, h in baseline.items())
    all_requests = [r for a in audits.values() for r in a["requests"]]
    all_choices = [r for a in audits.values() for r in a["choices"]]
    all_outcomes = [r for a in audits.values() for r in a["outcomes"]]
    for name, rows in [("requests", all_requests), ("choices", all_choices), ("outcomes", all_outcomes)]:
        emit(f"{name}.json", rows)
    summary = {"analysis_script_sha256": sha(Path(__file__)),
               "scope": {"groups": 20, "scientific_choices": 40, "engineering_controls": 1,
                         "code_scientific_choices": 20, "model_scientific_choices": 20, "model_groups": 10,
                         "models": 11, "repetitions": 5, "choices_per_model": 100, "outcomes_per_model": 50,
                         "recent_independent_review_choices": 18, "recent_independent_review_model_choices": 14},
               "cohorts": {n: {"execution": a["execution"], "verification": a["verification"]} for n, a in audits.items()},
               "models": models,
               "totals": {"requests": len(all_requests), "successful_requests": sum(r["status"] == "complete" for r in all_requests),
                          "http_status_counts": dict(Counter(str(r["http_status"]) for r in all_requests)),
                          "choice_categories": dict(Counter(r["category"] for r in all_choices)),
                          "semantic_fixed": fraction(sum(r["correct"] for r in all_choices), len(all_choices)),
                          "outcomes_exact": fraction(sum(r["exact"] for r in all_outcomes), len(all_outcomes)),
                          "labels_exact": fraction(sum(r["label_exact"] for r in all_outcomes), len(all_outcomes))},
               "cost": {"server_reported": aggregate([r["reported_cost_usd"] for r in all_requests]),
                        "usage_estimate": aggregate([r["usage_estimate_usd"] for r in all_requests]),
                        "selected_reported_else_estimated": aggregate([r["selected_cost_usd"] for r in all_requests]),
                        "estimate_only_subtotal_usd": sum(r["selected_cost_usd"] for r in all_requests if r["selected_cost_basis"] == "saved_usage_price_estimate"),
                        "unknown_job_ids": [r["job_id"] for r in all_requests if r["selected_cost_usd"] is None],
                        "billed_invoice_total_usd": None},
               "verification": {"network": "disabled", "new_model_calls": 0, "credential_files_read": 0,
                                "cohort_inputs_references_and_packets_equal": True, "shared_dataset_derive_scoring_bytes_equal": True,
                                "original_six_accounting_matches_previous_reconciliation": True,
                                "preexisting_baseline_files_unchanged": len(baseline),
                                "attempt_artifacts_matched": sum(a["verification"]["attempt_artifacts"] for a in audits.values()),
                                "expected_null_fields_preserved": sum(a["verification"]["null_fields_preserved"] for a in audits.values())},
               "code_only": audits["original"]["code_only"],
               "model_reference_options": audits["original"]["model_reference_options"],
               "model_reference_labels": audits["original"]["model_reference_labels"],
               "limitations": ["Development inputs; repeats do not increase independent task count.",
                               "Latency cohorts were executed at different times; effort and interfaces differ.",
                               "Missing usage or cache fields remain null; 429 charges are not assumed zero.",
                               "Integrity and score reproduction do not constitute scientific source review.",
                               "Human preparation, review, adaptation and local compute costs are unmeasured."]}
    emit("summary.json", summary)
    protected = {p: h for a in audits.values() for p, h in a["protected_sha256"].items()}
    protected.update({str(p.relative_to(ROOT)): sha(p) for p in (ROOT / "results/s2-execution-analysis-v1").glob("*") if p.is_file()})
    assert all(sha(ROOT / p) == h for p, h in protected.items())
    emit("protected-sha256.json", protected)
    print(json.dumps({"output": str(HERE.relative_to(ROOT)), "totals": summary["totals"], "cost": summary["cost"],
                      "verification": summary["verification"]}, indent=2))


if __name__ == "__main__":
    main()
