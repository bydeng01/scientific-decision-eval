"""One explicit Sonnet 8192-token condition after the preserved 2048-token failure."""

import argparse
import fcntl
import json
import math
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

from configure_science_keys import ROOT, load_key
from drag_baseline_control import price_upper_bound
from drag_matched_comparison import CAP, CASES, charge, parse_response, verify
from drag_pilot import append, read_lines, sha, verify_source, write_json


def prepare(out, source):
    verify_source(source)
    if (source / "pending.json").exists():
        raise SystemExit("Uncertain earlier request")
    old_ledger = read_lines(source / "api_ledger.jsonl")
    failures = [r for r in old_ledger if r["provider"] == "anthropic"]
    if len(failures) != 1 or failures[0]["case_id"] != CASES[0] or json.loads(failures[0]["raw_text"]).get("stop_reason") != "max_tokens":
        raise SystemExit("This amendment requires the documented single max_tokens failure")
    carry = read_lines(source / "carry_in.jsonl") + old_ledger
    if len(carry) != 12 or len({r["response_id"] for r in carry}) != 12:
        raise SystemExit("Unexpected carry-in count or duplicate response")
    plans = [p for p in json.loads((source / "plans.json").read_text()) if p["provider"] == "anthropic"]
    for plan in plans:
        plan["request"]["max_tokens"] = 8192
        plan["condition"] = "sonnet-low-8192"
        encoded = json.dumps(plan["request"], allow_nan=False).encode()
        if len(encoded) > 12000:
            raise SystemExit("Input outside reservation envelope")
        plan["reserve_usd"] = price_upper_bound("anthropic", {"input_tokens": len(encoded) + 2048, "output_tokens": 8192})
    bound = sum(charge(r) for r in carry) + sum(p["reserve_usd"] for p in plans)
    if bound > CAP:
        raise SystemExit("Entire amendment would exceed initial cap")
    out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source / "sources", out / "sources")
    for path in (Path(__file__), ROOT / "tests/test_drag_sonnet_completion.py",
                 ROOT / "scripts/drag_matched_comparison.py", ROOT / "scripts/drag_pilot.py",
                 ROOT / "scripts/drag_baseline_control.py", ROOT / "scripts/configure_science_keys.py"):
        shutil.copy2(path, out / "sources" / path.name)
    for name in ("requests.jsonl", "reference.jsonl"):
        shutil.copy2(source / name, out / name)
    (out / "carry_in.jsonl").write_bytes((source / "carry_in.jsonl").read_bytes() + (source / "api_ledger.jsonl").read_bytes())
    write_json(out / "plans.json", plans)
    files = [p for p in out.rglob("*") if p.is_file()]
    write_json(out / "manifest.json", {
        "scope": "Sonnet 8192-token completion diagnostic; original 2048 failure retained",
        "source": str(source.resolve()), "source_manifest_sha256": sha(source / "manifest.json"),
        "source_new_ledger_sha256": sha(source / "api_ledger.jsonl"),
        "carry_in_usd": sum(charge(r) for r in carry), "full_batch_reserved_upper_usd": bound,
        "initial_cap_usd": CAP, "total_budget_usd": 10,
        "cancelled_unattempted_original_slots": ["dev-00-r2", "dev-01-r1", "dev-01-r2"],
        "repeat_with_changed_setting": "dev-00-r1", "max_output_tokens": 8192,
        "sha256": {str(p.relative_to(out)): sha(p) for p in sorted(files)}})
    print(json.dumps({"prepared": str(out), "full_batch_upper_usd": bound}))


def run(out):
    verify(out)
    if sha(Path(__file__)) != sha(out / "sources" / Path(__file__).name):
        raise SystemExit("Amendment runner changed after freeze")
    with (out / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        pending, ledger_path = out / "pending.json", out / "api_ledger.jsonl"
        ledger = read_lines(ledger_path)
        if pending.exists() or any(r["status"] != "valid" or r.get("usage_cost_upper_estimate_usd") is None
                                  or charge(r) > r["reserve_usd"] for r in ledger):
            raise SystemExit("Stopped after earlier failure or pending request; no retry")
        attempted = {r["case_id"] for r in ledger}
        key = load_key("anthropic")
        if not key:
            raise SystemExit("Configured Anthropic key missing")
        for plan in json.loads((out / "plans.json").read_text()):
            if plan["case_id"] in attempted:
                continue
            if sum(charge(r) for r in read_lines(out / "carry_in.jsonl") + ledger) + plan["reserve_usd"] > CAP:
                raise SystemExit("Shared initial-stage cap would be exceeded")
            write_json(pending, plan)
            row, started = dict(plan), time.monotonic()
            try:
                req = urllib.request.Request(plan["endpoint"], data=json.dumps(plan["request"]).encode(), headers={
                    "Content-Type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"})
                with urllib.request.urlopen(req, timeout=180) as response:
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
                    row["probabilities"] = parse_response("anthropic", obj)
                    row["status"] = "valid"
                except (ValueError, KeyError, TypeError) as error:
                    row.update(status="invalid_response", error=str(error))
            estimate = None
            try:
                estimate = price_upper_bound("anthropic", row["usage"])
                if not math.isfinite(estimate) or estimate < 0:
                    estimate = None
            except (KeyError, TypeError):
                pass
            row.update(elapsed_seconds=time.monotonic() - started, reported_cost_usd=None,
                       usage_cost_upper_estimate_usd=estimate, budget_charge_usd=plan["reserve_usd"])
            row["reconciled_charge_usd"] = charge(row)
            append(ledger_path, row)
            ledger.append(row)
            if row["status"] != "transport_uncertain":
                pending.unlink()
            print(json.dumps({k: row.get(k) for k in ("provider", "condition", "case_id", "status", "probabilities",
                                                     "usage_cost_upper_estimate_usd", "elapsed_seconds")}), flush=True)
            if row["status"] != "valid" or estimate is None or estimate > plan["reserve_usd"]:
                raise SystemExit("Stopped after unexpected response or cost; no automatic retry")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source", type=Path, default=ROOT / "results/drag-matched-v1")
    args = parser.parse_args()
    prepare(args.output, args.source) if args.command == "prepare" else run(args.output)
