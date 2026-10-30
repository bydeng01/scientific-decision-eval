"""Run one frozen empty-data control per baseline, with a shared stage budget."""

import argparse
import fcntl
import json
import math
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

from configure_science_keys import load_key
from drag_pilot import LABELS, INSTRUCTIONS, CRITERIA, append, read_lines, sha, write_json, validate_distribution

SCHEMA = {"type": "object", "properties": {
    "probabilities": {"type": "object", "properties": {label: {"type": "number"} for label in LABELS},
                      "required": list(LABELS), "additionalProperties": False}},
    "required": ["probabilities"], "additionalProperties": False}
MODELS = {"openai": "gpt-6-astra", "anthropic": "claude-sonnet-5"}
ENDPOINTS = {"openai": "https://api.openai.com/v1/responses",
             "anthropic": "https://api.anthropic.com/v1/messages"}


def request_body(provider, case):
    instructions = INSTRUCTIONS + "\nAnswer definitions: " + json.dumps(CRITERIA)
    content = json.dumps(case["state"], allow_nan=False)
    if provider == "openai":
        return {"model": MODELS[provider], "instructions": instructions, "input": content,
                "reasoning": {"effort": "low"}, "max_output_tokens": 2048,
                "service_tier": "default", "store": False,
                "text": {"format": {"type": "json_schema", "name": "mechanism_probabilities",
                                     "strict": True, "schema": SCHEMA}}}
    return {"model": MODELS[provider], "system": instructions,
            "messages": [{"role": "user", "content": content}], "max_tokens": 2048,
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}}}


def price_upper_bound(provider, usage):
    # No tools, explicit cache writes, long context, or priority service.
    if provider == "openai":
        return (usage["input_tokens"] * 12.5 + usage["output_tokens"] * 50) / 1e6
    return (usage["input_tokens"] * 2 + usage.get("cache_creation_input_tokens", 0) * 4
            + usage.get("cache_read_input_tokens", 0) * 0.2 + usage["output_tokens"] * 10) / 1e6


def run(out, provider):
    manifest = json.loads((out / "manifest.json").read_text())
    for name, expected in manifest["sha256"].items():
        if sha(out / name) != expected:
            raise SystemExit(f"Frozen artifact changed: {name}")
    case = next(r for r in read_lines(out / "requests.jsonl") if r["id"] == "empty-prior")
    body = request_body(provider, case)
    encoded = json.dumps(body, allow_nan=False).encode()
    if len(encoded) > 12000:
        raise SystemExit("Request outside the bounded input size.")
    # UTF-8 bytes plus protocol allowance conservatively bound this ASCII input.
    reserve = price_upper_bound(provider, {"input_tokens": len(encoded) + 2048, "output_tokens": 2048})
    key = load_key(provider)
    if not key:
        raise SystemExit(f"{provider} key missing")
    with (out / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (out / "pending.json").exists() or list(out.glob("pending-control-*.json")):
            raise SystemExit("Uncertain earlier request; reconcile before continuing.")
        ledger_path = out / "api_ledger.jsonl"
        ledger = read_lines(ledger_path)
        if any(r["provider"] == provider for r in ledger):
            raise SystemExit("Control already attempted; no retry.")
        charged = sum(r["budget_charge_usd"] for r in ledger)
        if charged + reserve > 1:
            raise SystemExit("Shared USD 1 initial-stage budget would be exceeded.")
        snapshot = out / "sources/drag_baseline_control.py"
        if not snapshot.exists():
            shutil.copy2(__file__, snapshot)
        if sha(Path(__file__)) != sha(snapshot):
            raise SystemExit("Control runner changed after first request.")
        plan = {"provider": provider, "case_id": case["id"], "request": body,
                "endpoint": ENDPOINTS[provider], "reserve_usd": reserve,
                "source_sha256": sha(snapshot), "shared_initial_stage_cap_usd": 1.0,
                "scope": "empty-data interface and prior control only"}
        write_json(out / f"{provider}-control-plan.json", plan)
        pending = out / f"pending-control-{provider}.json"
        write_json(pending, plan)
        headers = {"Content-Type": "application/json"}
        if provider == "openai":
            headers["Authorization"] = "Bearer " + key
        else:
            headers.update({"x-api-key": key, "anthropic-version": "2023-06-01"})
        row = dict(plan)
        started = time.monotonic()
        try:
            req = urllib.request.Request(ENDPOINTS[provider], data=encoded, headers=headers)
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
                if provider == "openai":
                    if obj.get("status") != "completed":
                        raise ValueError("incomplete response")
                    txt = "".join(c.get("text", "") for item in obj["output"] if item["type"] == "message"
                                  for c in item["content"] if c["type"] == "output_text")
                else:
                    if obj.get("stop_reason") != "end_turn":
                        raise ValueError("incomplete response")
                    txt = "".join(c.get("text", "") for c in obj["content"] if c["type"] == "text")
                answer = json.loads(txt)
                probabilities = answer["probabilities"]
                row["probabilities"] = validate_distribution({"type": "choice", "probabilities": probabilities,
                                                            "choice": max(probabilities, key=probabilities.get)})
                row["status"] = "valid"
            except (ValueError, KeyError, TypeError) as error:
                row.update(status="invalid_response", error_type=type(error).__name__)
        row["elapsed_seconds"] = time.monotonic() - started
        row["reported_cost_usd"] = None
        estimate = None
        if row.get("usage"):
            try:
                estimate = price_upper_bound(provider, row["usage"])
                if not math.isfinite(estimate) or estimate < 0:
                    estimate = None
            except (KeyError, TypeError):
                pass
        row["usage_cost_upper_estimate_usd"] = estimate
        row["budget_charge_usd"] = max(reserve, estimate or 0)
        append(ledger_path, row)
        if row["status"] != "transport_uncertain":
            pending.unlink()
        print(json.dumps({k: row.get(k) for k in ("provider", "status", "probabilities", "usage_cost_upper_estimate_usd", "budget_charge_usd")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=MODELS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.output, args.provider)
