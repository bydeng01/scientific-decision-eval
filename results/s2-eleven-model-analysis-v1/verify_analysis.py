"""Check accounting boundaries, error attribution and byte-stable reproduction."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import analyze

HERE = Path(__file__).resolve().parent


def checks():
    names = []
    unknown = analyze.aggregate([None, None])
    assert unknown["known_subtotal"] is None and unknown["total"] is None
    assert analyze.aggregate([0, None]) == {"known_subtotal": 0, "known_records": 1, "missing_records": 1, "total": None}
    names.append("unreported_totals_stay_null_and_observed_zero_stays_zero")

    model = {"provider": "openai", "usd_per_million": {"input": .2, "cached_input": .02, "cache_write": .25, "output": 1.2}}
    usage = {"input_tokens": 1000, "output_tokens": 50}
    receipt = {"raw_body": json.dumps({"usage": usage}), "latency_seconds": 1}
    assert analyze.resources(model, receipt)["usage_estimate_usd"] is None
    usage["input_tokens_details"] = {"cached_tokens": 400, "cache_write_tokens": 100}
    usage["output_tokens_details"] = {"reasoning_tokens": 20}
    receipt["raw_body"] = json.dumps({"usage": usage})
    r = analyze.resources(model, receipt)
    assert abs(r["usage_estimate_usd"] - .000193) < 1e-14
    names.append("cache_write_field_reconciled_and_reasoning_not_billed_twice")

    model = {"provider": "anthropic", "usd_per_million": {"input": 5, "cached_input": .5, "cache_write": 6.25, "output": 25}}
    receipt["raw_body"] = json.dumps({"usage": {"input_tokens": 1000, "output_tokens": 50,
        "cache_read_input_tokens": 400, "cache_creation_input_tokens": 100,
        "output_tokens_details": {"thinking_tokens": 20}}})
    r = analyze.resources(model, receipt)
    assert abs(r["usage_estimate_usd"] - .007075) < 1e-14 and r["reasoning_or_thinking_tokens"] == 20
    names.append("anthropic_cache_is_additive_to_ordinary_input")

    lat = analyze.latency([None, 1, 2, 3, 4])
    assert lat["median"] == 2.5 and lat["p95_nearest_rank"] == 4 and lat["missing_records"] == 1
    names.append("latency_nearest_rank_and_missing_interval")
    try:
        analyze.socket.socket()
    except RuntimeError:
        pass
    else:
        raise AssertionError("Network guard did not block socket construction")
    names.append("socket_construction_blocked_before_network_access")

    s = analyze.read(HERE / "summary.json")
    choices = analyze.read(HERE / "choices.json")
    outcomes = analyze.read(HERE / "outcomes.json")
    requests = analyze.read(HERE / "requests.json")
    assert len(choices) == 1100 and len(outcomes) == len(requests) == 550
    assert {m["semantic_fixed"]["denominator"] for m in s["models"].values()} == {100}
    assert {m["model_dependent_outcomes_exact"]["denominator"] for m in s["models"].values()} == {50}
    assert sum(x["category"] == "semantic_error" for x in choices) == 7
    assert all(x["question_id"] == "B002-Q01" for x in choices if x["category"] == "semantic_error")
    assert sum(x["prediction"] is None for x in choices) == 24
    assert not any(x["prediction"] in {"not_stated", "other", "conflicting"} for x in choices)
    names.append("fixed_model_denominators_and_operational_vs_semantic_errors")
    for c in choices:
        if c["category"] == "semantic_error":
            o = next(o for o in outcomes if o["job_id"] == c["job_id"])
            assert not o["exact"] and not o["counts_exact"] and o["label_exact"]
    names.append("all_seven_semantic_errors_are_masked_by_final_label")
    terra = next(r for r in requests if r["job_id"] == "r01-B002-terra")
    assert terra["transport_error"] == "InterruptedWithoutReceipt" and terra["raw_body_sha256"] is None
    failures = [r for r in requests if r["http_status"] == 429]
    assert len(failures) == 11 and all(r["selected_cost_usd"] is None for r in failures)
    assert s["cost"]["selected_reported_else_estimated"]["total"] is None
    names.append("interrupted_and_rate_limited_request_costs_remain_unknown")
    assert s["models"]["qwen_flash"]["latency_successful"]["median"] > s["models"]["qwen_flash"]["latency_all_terminal"]["median"]
    names.append("success_latency_excludes_short_error_responses")
    return names


before = {p.name: analyze.sha(p) for p in HERE.glob("*") if p.is_file() and p.name != "verification.json"}
subprocess.run([sys.executable, "-B", str(HERE / "analyze.py")], check=True)
subprocess.run([sys.executable, "-B", str(HERE / "render_report.py")], check=True)
after = {p.name: analyze.sha(p) for p in HERE.glob("*") if p.is_file() and p.name != "verification.json"}
assert before == after
passed = checks()
protected = analyze.read(HERE / "protected-sha256.json")
assert all(analyze.sha(analyze.ROOT / p) == digest for p, digest in protected.items())
analyze.emit("verification.json", {"checks_passed": passed, "reproduction_byte_identical": True,
                                 "protected_files_unchanged": len(protected), "artifact_sha256": after})
print(json.dumps({"checks_passed": len(passed), "byte_identical_files": len(after), "protected_files": len(protected)}))
