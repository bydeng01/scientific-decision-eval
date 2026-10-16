"""Freeze and run the bounded, exposed-case drag comparison; preserve raw lanes."""

import argparse
import fcntl
import json
import math
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from configure_science_keys import ROOT, load_key
from drag_baseline_control import ENDPOINTS, MODELS, price_upper_bound, request_body
from drag_pilot import LABELS, append, read_lines, score, sha, validate_distribution, verify_source, write_json

CASES = ("dev-00-r1", "dev-00-r2", "dev-01-r1", "dev-01-r2")
CAP = 1.0


def known_cost(row):
    for field in ("reported_cost_usd", "usage_cost_upper_estimate_usd"):
        value = row.get(field)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0:
            return value
    return None


def charge(row):
    value = known_cost(row)
    if row["status"] == "transport_uncertain" or value is None:
        return row["reserve_usd"] if "reserve_usd" in row else row["budget_charge_usd"]
    return value


def rounding_sensitivity(values, reference):
    p = np.asarray(values, dtype=float)
    if p.shape != (3,) or not np.all(np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("invalid values")
    if not np.allclose(p * 100, np.round(p * 100), atol=1e-9, rtol=0):
        raise ValueError("not a two-decimal vector")
    lower, upper = np.maximum(0, p - .005), np.minimum(1, p + .005)
    if lower.sum() > 1 + 1e-12 or upper.sum() < 1 - 1e-12:
        raise ValueError("rounding intervals do not meet the simplex")
    # Projection of p onto the box-constrained simplex has q_i=clip(p_i+lambda).
    left, right = -.01, .01
    for _ in range(80):
        middle = (left + right) / 2
        if np.clip(p + middle, lower, upper).sum() < 1:
            left = middle
        else:
            right = middle
    q = np.clip(p + (left + right) / 2, lower, upper)
    # Minimize sum(t_i)/2 subject to |q_i-reference_i|<=t_i, sum(q)=1.
    eye = np.eye(3)
    fit = linprog([0, 0, 0, .5, .5, .5],
                  A_ub=np.vstack([np.hstack([eye, -eye]), np.hstack([-eye, -eye])]),
                  b_ub=np.r_[reference, -np.asarray(reference)],
                  A_eq=[[1, 1, 1, 0, 0, 0]], b_eq=[1],
                  bounds=list(zip(lower, upper)) + [(0, None)] * 3, method="highs")
    if not fit.success:
        raise ValueError("rounding bound optimization failed")
    return {"raw_sum": float(p.sum()), "lower": lower.tolist(), "upper": upper.tolist(),
            "derived_probabilities": q.tolist(), "minimum_tv_to_reference": float(fit.fun),
            "reference_inside_rounding_intervals": bool(np.all(np.asarray(reference) >= lower - 1e-12)
                                                        and np.all(np.asarray(reference) <= upper + 1e-12))}


def verify(out):
    manifest = json.loads((out / "manifest.json").read_text())
    for name, expected in manifest["sha256"].items():
        if sha(out / name) != expected:
            raise SystemExit(f"Frozen artifact changed: {name}")
    for name in ("drag_matched_comparison.py", "drag_pilot.py", "drag_baseline_control.py", "configure_science_keys.py"):
        if sha(ROOT / "scripts" / name) != sha(out / "sources" / name):
            raise SystemExit(f"Live source changed: {name}")
    return manifest


def prepare(out, source):
    verify_source(source)
    if list(source.glob("pending*.json")):
        raise SystemExit("Uncertain earlier request")
    carry = read_lines(source / "api_ledger.jsonl")
    ids = [r.get("response_id") for r in carry if r.get("response_id")]
    if len(ids) != len(set(ids)):
        raise SystemExit("Duplicate response IDs in carry-in")
    requests = {r["id"]: r for r in read_lines(source / "requests.jsonl")}
    plans = []
    for case_id in CASES:
        for provider in MODELS:
            body = request_body(provider, requests[case_id])
            encoded = json.dumps(body, allow_nan=False).encode()
            if len(encoded) > 12000:
                raise SystemExit("Input outside reservation envelope")
            plans.append({"provider": provider, "case_id": case_id, "request": body,
                          "endpoint": ENDPOINTS[provider], "reserve_usd": price_upper_bound(
                              provider, {"input_tokens": len(encoded) + 2048, "output_tokens": 2048})})
    bound = sum(charge(r) for r in carry) + sum(p["reserve_usd"] for p in plans)
    if bound > CAP:
        raise SystemExit(f"Entire matched batch would exceed initial cap: {bound}")
    out.mkdir(parents=True, exist_ok=False)
    (out / "sources").mkdir()
    for name in ("requests.jsonl", "reference.jsonl"):
        shutil.copy2(source / name, out / name)
    shutil.copy2(source / "api_ledger.jsonl", out / "carry_in.jsonl")
    for path in (Path(__file__), ROOT / "scripts/drag_pilot.py", ROOT / "scripts/drag_baseline_control.py",
                 ROOT / "scripts/configure_science_keys.py", ROOT / "tests/test_drag_matched_comparison.py"):
        shutil.copy2(path, out / "sources" / path.name)
    write_json(out / "plans.json", plans)
    reconciliation = [{"provider": r["provider"], "case_id": r["case_id"],
                       "original_charge_usd": r["budget_charge_usd"], "reconciled_charge_usd": charge(r),
                       "response_id": r.get("response_id")} for r in carry]
    write_json(out / "budget_reconciliation.json", reconciliation)
    files = [p for p in out.rglob("*") if p.is_file()]
    write_json(out / "manifest.json", {"source": str(source.resolve()),
        "scope": "matched exposed development diagnostic: two systems, four states, eight new calls",
        "case_ids": list(CASES), "total_budget_usd": 10, "initial_cap_usd": CAP,
        "carry_in_usd": sum(charge(r) for r in carry), "full_batch_reserved_upper_usd": bound,
        "sha256": {str(p.relative_to(out)): sha(p) for p in sorted(files)}})
    print(json.dumps({"prepared": str(out), "new_calls": len(plans), "full_batch_upper_usd": bound}))


def parse_response(provider, obj):
    if obj.get("model") != MODELS[provider]:
        raise ValueError("unrecognized returned model")
    if provider == "openai":
        if obj.get("status") != "completed":
            raise ValueError("incomplete response")
        txt = "".join(c.get("text", "") for item in obj["output"] if item["type"] == "message"
                      for c in item["content"] if c["type"] == "output_text")
    else:
        if obj.get("stop_reason") != "end_turn":
            raise ValueError("incomplete response")
        txt = "".join(c.get("text", "") for c in obj["content"] if c["type"] == "text")
    p = json.loads(txt)["probabilities"]
    return validate_distribution({"type": "choice", "probabilities": p, "choice": max(p, key=p.get)})


def run(out, provider, limit):
    verify(out)
    with (out / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        pending = out / "pending.json"
        if pending.exists():
            raise SystemExit("Uncertain earlier request; no new calls")
        ledger_path = out / "api_ledger.jsonl"
        ledger = read_lines(ledger_path)
        if any(r["status"] == "transport_uncertain" for r in ledger):
            raise SystemExit("Uncertain earlier request in ledger; no new calls")
        if any(r["provider"] == provider and (r["status"] != "valid" or known_cost(r) is None
                    or charge(r) > r["reserve_usd"]) for r in ledger):
            raise SystemExit("Provider stopped after earlier failure; no retry")
        attempted = {(r["provider"], r["case_id"]) for r in ledger}
        plans = [p for p in json.loads((out / "plans.json").read_text())
                 if p["provider"] == provider and (provider, p["case_id"]) not in attempted][:limit]
        key = load_key(provider)
        if not key:
            raise SystemExit("Configured provider key missing")
        for plan in plans:
            spent = sum(charge(r) for r in read_lines(out / "carry_in.jsonl") + ledger)
            if spent + plan["reserve_usd"] > CAP:
                raise SystemExit("Shared initial-stage cap would be exceeded")
            write_json(pending, plan)
            headers = {"Content-Type": "application/json"}
            if provider == "openai":
                headers["Authorization"] = "Bearer " + key
            else:
                headers.update({"x-api-key": key, "anthropic-version": "2023-06-01"})
            row = dict(plan)
            started = time.monotonic()
            try:
                req = urllib.request.Request(plan["endpoint"], data=json.dumps(plan["request"]).encode(), headers=headers)
                with urllib.request.urlopen(req, timeout=55) as response:
                    raw = response.read().decode()
            except urllib.error.HTTPError as error:
                row.update(status="http_error", http_status=error.code,
                           raw_text=error.read().decode(errors="replace").replace(key, "[REDACTED]"))
            except Exception as error:
                row.update(status="transport_uncertain", error_type=type(error).__name__)
            else:
                row["raw_text"] = raw.replace(key, "[REDACTED]")
                try:
                    obj = json.loads(raw)
                    row.update(returned_model=obj.get("model"), response_id=obj.get("id"), usage=obj.get("usage"))
                    row["probabilities"] = parse_response(provider, obj)
                    row["status"] = "valid"
                except (ValueError, KeyError, TypeError) as error:
                    row.update(status="invalid_response", error=str(error))
            row["elapsed_seconds"] = time.monotonic() - started
            estimate = None
            try:
                estimate = price_upper_bound(provider, row["usage"])
                if not math.isfinite(estimate) or estimate < 0:
                    estimate = None
            except (KeyError, TypeError):
                pass
            row.update(reported_cost_usd=None, usage_cost_upper_estimate_usd=estimate,
                       budget_charge_usd=plan["reserve_usd"])
            row["reconciled_charge_usd"] = charge(row)
            append(ledger_path, row)
            ledger.append(row)
            if row["status"] != "transport_uncertain":
                pending.unlink()
            print(json.dumps({k: row.get(k) for k in ("provider", "case_id", "status", "probabilities",
                                                     "usage_cost_upper_estimate_usd", "elapsed_seconds")}), flush=True)
            if row["status"] != "valid" or estimate is None or estimate > plan["reserve_usd"]:
                raise SystemExit("Stopped after unexpected response or cost; no automatic retry")


def analyze(out):
    verify(out)
    refs = {r["id"]: r for r in read_lines(out / "reference.jsonl")}
    ledger = read_lines(out / "carry_in.jsonl") + read_lines(out / "api_ledger.jsonl")
    rows = []
    for r in ledger:
        case_id, provider = r["case_id"], r["provider"]
        row = {"provider": provider, "case_id": case_id, "native_status": r["status"]}
        if r["status"] == "valid":
            row.update(probabilities=r["probabilities"], native_scores=score(r["probabilities"], refs[case_id]))
        if provider == "openrouter-jev":
            raw_answer = json.loads(r["raw_text"])["answers"]["mechanism"]
            p = [raw_answer["probabilities"][label] for label in LABELS]
            row["raw_probabilities"] = p
            row["rounding_sensitivity"] = rounding_sensitivity(p, refs[case_id]["posterior"])
            row["rounding_sensitivity"]["scores"] = score(row["rounding_sensitivity"]["derived_probabilities"], refs[case_id])
        rows.append(row)
    write_json(out / "analysis.json", {"scope": "four exposed states; full 24-state screen incomplete",
        "rows": rows, "cost_usd": sum(charge(r) for r in ledger), "distinct_api_attempts": len(ledger),
        "new_attempts": len(read_lines(out / "api_ledger.jsonl"))})
    print(json.dumps({"analysis": str(out / "analysis.json"), "cost_usd": sum(charge(r) for r in ledger),
                      "distinct_api_attempts": len(ledger)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run", "analyze"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=ROOT / "results/drag-development-v2")
    parser.add_argument("--provider", choices=MODELS)
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.output, args.source)
    elif args.command == "analyze":
        analyze(args.output)
    else:
        if args.provider is None or args.limit < 1:
            parser.error("run requires --provider and a positive --limit")
        run(args.output, args.provider, args.limit)
