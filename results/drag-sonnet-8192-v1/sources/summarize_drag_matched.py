"""Report paired native scores separately from the explicit rounding sensitivity."""

import argparse
import json
from pathlib import Path

import numpy as np

from drag_matched_comparison import CASES, analyze, charge
from drag_pilot import read_lines, score, sha, write_json


def aggregate(scores, refs):
    if not scores:
        return {"n": 0}
    episodes = sorted({refs[c]["episode"] for c in scores})
    complete = [e for e in episodes if all(f"{e}-r{r}" in scores for r in (1, 2))]
    result = {"n": len(scores), "episodes": len(episodes), "complete_episodes": len(complete)}
    for key in ("correct", "brier", "log_loss", "tv", "retained_size"):
        result["mean_" + key] = float(np.mean([s[key] for s in scores.values()]))
    result["median_tv"] = float(np.median([s["tv"] for s in scores.values()]))
    for key in ("excluded", "confident_wrong", "zero_true_probability"):
        result[key + "_states"] = sum(s[key] for s in scores.values())
    result["any_exclusion_complete_episodes"] = sum(any(scores[f"{e}-r{r}"]["excluded"] for r in (1, 2)) for e in complete)
    result["any_confident_wrong_complete_episodes"] = sum(any(scores[f"{e}-r{r}"]["confident_wrong"] for r in (1, 2)) for e in complete)
    first = []
    for e in complete:
        candidates = [scores[f"{e}-r{r}"] for r in (1, 2) if scores[f"{e}-r{r}"]["confident"]]
        if candidates:
            first.append(candidates[0])
    result["first_crossing_episodes"] = len(first)
    result["wrong_at_first_crossing"] = sum(s["confident_wrong"] for s in first)
    return result


def summarize(out):
    analyze(out)
    analysis = json.loads((out / "analysis.json").read_text())
    manifest = json.loads((out / "manifest.json").read_text())
    amended = manifest.get("max_output_tokens") == 8192
    planned_calls = len(json.loads((out / "plans.json").read_text()))
    refs = {r["id"]: r for r in read_lines(out / "reference.jsonl")}
    ledger = read_lines(out / "carry_in.jsonl") + read_lines(out / "api_ledger.jsonl")
    by_key = {(r["provider"], r["case_id"]): r for r, raw in zip(analysis["rows"], ledger)
              if not (amended and r["provider"] == "anthropic" and r["case_id"] != "empty-prior"
                      and raw.get("condition") != "sonnet-low-8192")}
    failure_notes = {(r["provider"], r["case_id"]): "max_tokens (" + str(r["request"]["max_tokens"]) + ")"
                     for r in ledger if r["provider"] == "anthropic" and r["status"] == "invalid_response"
                     and json.loads(r.get("raw_text", "{}" )).get("stop_reason") == "max_tokens"}
    providers = ("openrouter-jev", "openai", "anthropic")
    common = [c for c in CASES if all(by_key.get((p, c), {}).get("native_status") == "valid" for p in providers)]
    methods = {"reference": {c: score(refs[c]["posterior"], refs[c]) for c in CASES},
               "uniform": {c: score([1/3]*3, refs[c]) for c in CASES}}
    for p in providers:
        name = p + " native" + (" (8192-token condition)" if amended and p == "anthropic" else "")
        methods[name] = {c: by_key[p, c]["native_scores"] for c in CASES
                                   if (p, c) in by_key and "native_scores" in by_key[p, c]}
    methods["Jev rounding sensitivity"] = {c: by_key["openrouter-jev", c]["rounding_sensitivity"]["scores"] for c in CASES}
    aggregates = {method: {"all_available": aggregate(scores, refs),
                          "round1": aggregate({c:s for c,s in scores.items() if refs[c]["round"] == 1}, refs),
                          "round2": aggregate({c:s for c,s in scores.items() if refs[c]["round"] == 2}, refs),
                          "common_native_states": aggregate({c:s for c,s in scores.items() if c in common}, refs)}
                  for method, scores in methods.items()}
    costs = {}
    cost_key = lambda r: r["provider"] + (" / " + r.get("condition", "2048-token condition") if r["provider"] == "anthropic" else "")
    for condition in dict.fromkeys(cost_key(r) for r in ledger):
        group = [r for r in ledger if cost_key(r) == condition]
        costs[condition] = {"calls": len(group), "charge_usd": sum(charge(r) for r in group),
                           "mean_latency_seconds": float(np.mean([r["elapsed_seconds"] for r in group])),
                           "trajectory_attempts": sum(r["case_id"] in CASES for r in group),
                           "trajectory_native_valid": sum(r["case_id"] in CASES and r["status"] == "valid" for r in group)}
    report = {"common_native_case_ids": common, "aggregates": aggregates, "costs": costs,
              "sonnet_output_cap": 8192 if amended else 2048, "openai_output_cap": 2048,
              "new_attempts": analysis["new_attempts"], "cumulative_cost_usd": analysis["cost_usd"],
              "analysis_sha256": sha(out / "analysis.json"), "report_source_sha256": sha(Path(__file__))}
    write_json(out / "report.json", report)
    lines = ["# Matched drag diagnostic", "",
             "Exposed development data: two systems (H1 and H2), four accumulated-data states.",
             "No H3-generated system was attempted. These cases are not a population benchmark.", "",
             "## Individual responses", "",
             "All vectors below are H1 / H2 / H3, displayed to four decimals; JSON retains full precision.",
             "An asterisk marks a native-invalid vector.", "",
             "| State | True law | Reference | Jev raw | Astra | Sonnet |",
             "|---|---|---|---|---|---|"]
    if amended:
        lines[5:5] = ["Astra uses a 2048-token output cap; Sonnet uses the separate 8192-token condition.",
                       "Sonnet's first 2048-token trajectory attempt ended at max_tokens without probabilities.",
                       "That failure is retained in carry_in.jsonl. The table uses the new condition only.", ""]
    vector = lambda p: " / ".join(f"{v:.4f}" for v in p)
    for c in CASES:
        cells = [c, refs[c]["truth"], vector(refs[c]["posterior"])]
        for provider in providers:
            row = by_key.get((provider, c), {})
            p = row.get("raw_probabilities", row.get("probabilities"))
            cells.append(vector(p) + (" *" if row["native_status"] != "valid" else "") if p is not None
                         else failure_notes.get((provider, c), row.get("native_status", "not attempted")))
        lines.append("| " + " | ".join(cells) + " |")
    lines += ["", "## Probability precision", "",
              "Native validity is unchanged: Jev dev-01-r2 sums to 0.99 and is invalid.",
              "The following bounds assume independent ±0.005 rounding intervals intersected",
              "with the simplex. This assumption is not a verified vendor precision policy.", "",
              "| State | Derived sensitivity vector | Minimum possible TV to reference |",
              "|---|---|---:|"]
    for c in ("empty-prior",) + CASES:
        s = by_key["openrouter-jev", c]["rounding_sensitivity"]
        lines.append(f"| {c} | {vector(s['derived_probabilities'])} | {s['minimum_tv_to_reference']:.6f} |")
    lines += ["", "## Native scores on common valid states", "",
              "Common states: " + (", ".join(common) if common else "none") + ".", "",
              "| Method | n | Accuracy | Brier | Mean TV | Mean retained size |",
              "|---|---:|---:|---:|---:|---:|"]
    for method, groups in aggregates.items():
        if method == "Jev rounding sensitivity":
            continue
        a = groups["common_native_states"]
        if a["n"]:
            lines.append(f"| {method} | {a['n']} | {a['mean_correct']:.3f} | {a['mean_brier']:.6g} | "
                         f"{a['mean_tv']:.6g} | {a['mean_retained_size']:.2f} |")
    lines += ["", "## Available states by round", "",
              "Sample counts differ for native Jev. Its derived sensitivity lane is separate.", "",
              "| Method | Round | n | Accuracy | Brier | Mean TV | True law excluded | Confident wrong |",
              "|---|---|---:|---:|---:|---:|---:|---:|"]
    for method, groups in aggregates.items():
        for round_id in (1, 2):
            a = groups[f"round{round_id}"]
            if a["n"]:
                lines.append(f"| {method} | {round_id} | {a['n']} | {a['mean_correct']:.3f} | {a['mean_brier']:.6g} | "
                             f"{a['mean_tv']:.6g} | {a['excluded_states']} | {a['confident_wrong_states']} |")
    lines += ["", "## Completeness and cost", "",
              f"New attempts in this condition: {analysis['new_attempts']}/{planned_calls}. Cumulative distinct API attempts: {len(ledger)}.",
              f"Cumulative reported-plus-usage-estimated charge: USD {analysis['cost_usd']:.9f}.",
              "Provider usage estimates are not reconciled invoices. Every input/output reservation",
              "and the release of unused earlier reservations is recorded separately.", "",
              "| Provider | Calls including control | Valid / attempted trajectory states | Charge USD | Mean latency s |",
              "|---|---:|---|---:|---:|"]
    for p, c in costs.items():
        lines.append(f"| {p} | {c['calls']} | {c['trajectory_native_valid']} / {c['trajectory_attempts']} | "
                     f"{c['charge_usd']:.9f} | {c['mean_latency_seconds']:.2f} |")
    lines += ["", "The planned full 24-state-per-model screen remains incomplete. Its all-valid",
              "native Jev advancement condition cannot pass with the preserved failure.",
              "No calibration or test episodes were generated.",
              ("Sonnet dev-00-r1 was repeated once under the changed output cap; its original failure remains."
               if amended else "No response was retried in this original condition."),
              "No sampling interval, rare-error guarantee, or repeat variability is estimated.",
              "Episode-level exclusion, first-crossing counts, log loss, and exact-zero counts",
              "are in report.json; states within a system are not independent samples."]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"summary": str(out / "summary.md"), "common_native_cases": len(common)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    summarize(parser.parse_args().output)
