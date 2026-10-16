"""Summarize existing drag API usage and client latency without making requests."""

import argparse
import json
import shutil
import statistics
from pathlib import Path

from drag_matched_comparison import CASES, charge
from drag_pilot import read_lines, sha, write_json


def resource_row(row):
    usage = row["usage"]
    details = usage.get("output_tokens_details", {})
    reasoning = details.get("reasoning_tokens", details.get("thinking_tokens"))
    input_details = usage.get("input_tokens_details", {})
    if row["provider"] == "openrouter-jev":
        condition = "Jev 1.13 / native Choice"
    elif row["provider"] == "openai":
        condition = "Astra / low / 2048 cap"
    else:
        condition = f"Sonnet / low / {row['request']['max_tokens']} cap"
    return {
        "condition": condition, "provider": row["provider"], "case_id": row["case_id"],
        "response_id": row["response_id"], "returned_model": row["returned_model"],
        "status": row["status"], "input_tokens": usage["input_tokens"],
        "output_tokens_including_reported_reasoning": usage["output_tokens"],
        "reasoning_or_thinking_tokens": reasoning,
        "cache_read_tokens": input_details.get("cached_tokens", usage.get("cache_read_input_tokens")),
        "cache_creation_tokens": input_details.get("cache_write_tokens", usage.get("cache_creation_input_tokens")),
        "client_elapsed_seconds": row["elapsed_seconds"],
        "reported_or_conservative_estimated_cost_usd": charge(row),
        "dollar_cost_source": "provider_reported" if row.get("reported_cost_usd") is not None else "usage_price_upper_estimate",
    }


def aggregate(rows):
    if not rows:
        return None
    reasoning = [r["reasoning_or_thinking_tokens"] for r in rows]
    elapsed = [r["client_elapsed_seconds"] for r in rows]
    return {
        "attempts": len(rows), "valid_outputs": sum(r["status"] == "valid" for r in rows),
        "case_ids": [r["case_id"] for r in rows],
        "input_tokens_total": sum(r["input_tokens"] for r in rows),
        "output_tokens_total": sum(r["output_tokens_including_reported_reasoning"] for r in rows),
        "reasoning_or_thinking_tokens_total": sum(reasoning) if all(v is not None for v in reasoning) else None,
        "mean_input_tokens": statistics.mean(r["input_tokens"] for r in rows),
        "mean_output_tokens": statistics.mean(r["output_tokens_including_reported_reasoning"] for r in rows),
        "sum_client_elapsed_seconds": sum(elapsed), "mean_client_elapsed_seconds": statistics.mean(elapsed),
        "median_client_elapsed_seconds": statistics.median(elapsed),
        "min_client_elapsed_seconds": min(elapsed), "max_client_elapsed_seconds": max(elapsed),
        "reported_or_conservative_estimated_cost_usd": sum(r["reported_or_conservative_estimated_cost_usd"] for r in rows),
    }


def report(source, out):
    if (source / "pending.json").exists():
        raise SystemExit("Pending request: wait for reconciliation before a final resource report")
    for name in ("manifest.json", "completion_manifest.json"):
        manifest = json.loads((source / name).read_text())
        for path, expected in manifest["sha256"].items():
            if sha(source / path) != expected:
                raise SystemExit(f"Frozen artifact changed: {path}")
    ledger = read_lines(source / "carry_in.jsonl") + read_lines(source / "api_ledger.jsonl")
    if len({r["response_id"] for r in ledger}) != len(ledger):
        raise SystemExit("Duplicate response IDs")
    rows = [resource_row(r) for r in ledger]
    groups = {}
    for condition in dict.fromkeys(r["condition"] for r in rows):
        group = [r for r in rows if r["condition"] == condition]
        tasks = [r for r in group if r["case_id"] in CASES]
        groups[condition] = {
            "all_attempts_including_controls": aggregate(group),
            "trajectory_attempts_including_failures": aggregate(tasks),
            "covers_exactly_four_matched_states": len(tasks) == 4 and {r["case_id"] for r in tasks} == set(CASES),
        }
    out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, out / "reporter_snapshot.py")
    write_json(out / "resources.json", {
        "scope": "offline accounting of all 16 prior drag calls; no new API requests",
        "latency_definition": "client elapsed around request construction/network/read/response parsing; includes network, gateway, and queueing; excludes task preprocessing and downstream scientific actions",
        "token_definition": "provider-reported input/output accounting; reported reasoning is a subset of output, never added twice; missing reasoning metadata means unknown",
        "comparison_boundary": "different tokenizers, service paths and compute settings; not FLOPs or isolated model latency; four paired states are too few for stable tail-latency estimates",
        "preprocessing_and_candidate_generation_cost": "not instrumented separately in the original experiment",
        "all_attempts": aggregate(rows), "conditions": groups, "per_request": rows,
        "source_files_sha256": {str((source / name).resolve()): sha(source / name)
                                for name in ("carry_in.jsonl", "api_ledger.jsonl", "manifest.json", "completion_manifest.json")},
    })
    lines = ["# Drag pilot: tokens and latency", "",
             "This is an offline supplement to the completed diagnostic. No new API calls were made.", "",
             "The comparison below uses the same four trajectory states for each setting and includes",
             "invalid/incomplete attempts. Empty-prior controls are excluded. The earlier Sonnet",
             "2048-token failure is retained separately and included in cumulative accounting.", "",
             "| Setting | Valid / attempted | Mean input tokens | Mean output tokens | Mean client seconds | Median seconds | Total charge USD |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for condition, group in groups.items():
        if group["covers_exactly_four_matched_states"]:
            g = group["trajectory_attempts_including_failures"]
            lines.append(f"| {condition} | {g['valid_outputs']} / {g['attempts']} | {g['mean_input_tokens']:.2f} | "
                         f"{g['mean_output_tokens']:.2f} | {g['mean_client_elapsed_seconds']:.3f} | "
                         f"{g['median_client_elapsed_seconds']:.3f} | {g['reported_or_conservative_estimated_cost_usd']:.9f} |")
    lines += ["", "## Accounting across all conditions", "",
              "The following includes controls, failed requests, and the changed-setting repeat.", "",
              "| Setting | Calls | Input tokens | Output tokens | Reported reasoning/thinking tokens within output | Sum of client seconds | Charge USD |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for condition, group in groups.items():
        g = group["all_attempts_including_controls"]
        reasoning = g["reasoning_or_thinking_tokens_total"]
        lines.append(f"| {condition} | {g['attempts']} | {g['input_tokens_total']} | {g['output_tokens_total']} | "
                     f"{reasoning if reasoning is not None else 'not reported'} | {g['sum_client_elapsed_seconds']:.3f} | "
                     f"{g['reported_or_conservative_estimated_cost_usd']:.9f} |")
    total = aggregate(rows)
    lines += ["", f"Cumulative charge: USD {total['reported_or_conservative_estimated_cost_usd']:.9f} across {len(rows)} distinct paid requests.", "",
              "Output tokens already include reported reasoning/thinking tokens. Do not add those",
              "tokens again. Jev does not report an internal reasoning-token breakdown here; this",
              "does not establish zero internal computation. Token counts use each provider's",
              "accounting and do not measure equal computational work across models.", "",
              "Elapsed time is client-observed request time, including network, gateway, queueing,",
              "and response handling. Jev uses OpenRouter; the baselines use direct provider APIs.",
              "This is not isolated model inference time. The summed request durations exclude gaps",
              "between calls and are not total project wall time. Preprocessing, candidate generation,",
              "and downstream actions were not timed separately in the original pilot.", "",
              "Four states from two systems do not support stable p95/p99 or throughput estimates.",
              "Quality scores and response failures must accompany speed/cost comparisons; these",
              "measurements do not establish a useful quality-efficiency operating point for Jev.",
              "See ../drag-sonnet-8192-v1/summary.md for quality scores and the retained failures."]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    files = sorted(p for p in out.iterdir() if p.is_file())
    write_json(out / "manifest.json", {"scope": "derived resource accounting only",
                                        "sha256": {p.name: sha(p) for p in files}})
    print("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("results/drag-sonnet-8192-v1"))
    parser.add_argument("--output", type=Path, default=Path("results/drag-resource-audit-v1"))
    args = parser.parse_args()
    report(args.source, args.output)
