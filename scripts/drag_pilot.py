"""Prepare and inspect a finite-prior drag experiment; paid Jev calls are explicit."""

import argparse
import fcntl
import hashlib
import itertools
import json
import math
import platform
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import scipy
from scipy.special import logsumexp

from configure_science_keys import ROOT, load_key

LABELS = ("H1", "H2", "H3")
TIMES = [0.1, 0.3, 0.6, 1.0, 1.6, 2.5]
SIGMA = 0.04
PARAMS = {
    "H1": [(a, 0.0) for a in (0.2, 0.4, 0.8)],
    "H2": [(0.0, b) for b in (0.2, 0.4, 0.8)],
    "H3": list(itertools.product((0.1, 0.2, 0.4), repeat=2)),
}
ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.13"
RESERVE = 0.01
INSTRUCTIONS = (
    "Infer which physical law generated the observations under the explicitly "
    "specified prior and observation model. Return probabilities over H1, H2, H3 "
    "that approximate the posterior given ALL observations. Integrate over the "
    "listed parameter possibilities, keeping the same parameters across experiments. "
    "The three hypotheses are exhaustive. When evidence is weak, distribute "
    "probability across plausible hypotheses instead of committing to one."
)
CRITERIA = {
    "H1": "Linear drag: dv/dt = -a*v, b=0.",
    "H2": "Quadratic drag: dv/dt = -b*v*abs(v), a=0.",
    "H3": "Mixed drag: dv/dt = -a*v - b*v*abs(v), a>0 and b>0.",
}


def velocity(t, v0, a, b):
    t = np.asarray(t, dtype=float)
    if a == 0:
        return v0 / (1 + b * v0 * t)
    return v0 * np.exp(-a * t) / (1 + b * v0 / a * (-np.expm1(-a * t)))


def posterior(experiments):
    log_evidence = []
    for label in LABELS:
        log_likelihoods = []
        for a, b in PARAMS[label]:
            ll = 0.0
            for experiment in experiments:
                mu = velocity(experiment["times"], experiment["initial_velocity"], a, b)
                residual = (np.asarray(experiment["observed_velocity"]) - mu) / SIGMA
                ll -= 0.5 * float(residual @ residual)
            log_likelihoods.append(ll)
        log_evidence.append(logsumexp(log_likelihoods) - math.log(len(log_likelihoods)))
    return np.exp(np.array(log_evidence) - logsumexp(log_evidence))


def state(experiments):
    return {
        "task": "Identify a dimensionless drag law from independent noisy velocity measurements.",
        "model_priors": {label: 1 / 3 for label in LABELS},
        "parameter_priors": {
            label: {"distribution": "uniform over listed (a,b) pairs",
                    "pairs": PARAMS[label]} for label in LABELS
        },
        "observation_model": {
            "noise": "independent additive Gaussian noise at each observation",
            "known_standard_deviation": SIGMA,
            "initial_velocity": "known exactly; no measurement at t=0 is included",
            "shared_parameters": "one fixed (a,b) for all experiments in this state",
        },
        "analytic_solution_for_positive_initial_velocity": {
            "a_positive": "v(t)=v0*exp(-a*t)/(1+(b*v0/a)*(1-exp(-a*t)))",
            "a_zero": "v(t)=v0/(1+b*v0*t)",
        },
        "experiments": experiments,
    }


def generate(seed=20260920):
    rng = np.random.default_rng(seed)
    requests = [{"id": "empty-prior", "state": state([])}]
    truth = [{"id": "empty-prior", "episode": None, "round": 0,
              "truth": None, "posterior": posterior([]).tolist()}]
    for draw, label in itertools.product(range(4), LABELS):
        episode = f"dev-{draw * 3 + LABELS.index(label):02d}"
        a, b = PARAMS[label][int(rng.integers(len(PARAMS[label])))]
        experiments = []
        for round_id, v0 in enumerate((0.6, 3.0), start=1):
            y = velocity(TIMES, v0, a, b) + rng.normal(0, SIGMA, len(TIMES))
            experiments = experiments + [{"initial_velocity": v0, "times": TIMES,
                                           "observed_velocity": y.tolist()}]
            request_id = f"{episode}-r{round_id}"
            requests.append({"id": request_id, "state": state(experiments)})
            truth.append({"id": request_id, "episode": episode, "round": round_id,
                          "truth": label, "parameters": [a, b],
                          "posterior": posterior(experiments).tolist()})
    return requests, truth


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def read_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def append(path, row):
    with path.open("a") as stream:
        stream.write(json.dumps(row, allow_nan=False) + "\n")
        stream.flush()
        import os
        os.fsync(stream.fileno())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_source(source):
    """Check a published source against release hashes, or a new run against its freeze."""
    source = source.resolve()
    relative = source.relative_to(ROOT).as_posix() if source.is_relative_to(ROOT) else None
    release = ROOT / "release-sha256.json"
    files = json.loads(release.read_text())["files"] if relative and release.is_file() else {}
    manifest_key = f"{relative}/manifest.json"
    if manifest_key in files:
        expected = {name: digest for name, digest in files.items()
                    if name.startswith(relative + "/")}
        actual = {p.relative_to(ROOT).as_posix() for p in source.rglob("*") if p.is_file()}
        if actual != set(expected):
            raise SystemExit(f"Published source file inventory changed: {relative}")
        for name, digest in expected.items():
            path = ROOT / name
            if not path.is_file() or sha(path) != digest:
                raise SystemExit(f"Published source changed: {name}")
    else:
        manifest = json.loads((source / "manifest.json").read_text())
        for name, digest in manifest["sha256"].items():
            path = source / name
            if not path.is_file() or sha(path) != digest:
                raise SystemExit(f"Source frozen artifact changed: {name}")
    return json.loads((source / "manifest.json").read_text())


def prepare(out):
    requests, truth = generate()
    weak = sum(max(r["posterior"]) < 0.90 for r in truth if r["round"] == 1)
    strong = sum(max(r["posterior"]) > 0.90 for r in truth if r["round"] == 2)
    gate = weak >= 4 and strong >= 6
    out.mkdir(parents=True, exist_ok=False)
    for name, rows in (("requests.jsonl", requests), ("reference.jsonl", truth)):
        for row in rows:
            append(out / name, row)
    sources = out / "sources"
    sources.mkdir()
    for path in (Path(__file__), ROOT / "scripts/configure_science_keys.py",
                 ROOT / "tests/test_drag_pilot.py"):
        shutil.copy2(path, sources / path.name)
    names = ["requests.jsonl", "reference.jsonl"] + [str(p.relative_to(out)) for p in sorted(sources.iterdir())]
    write_json(out / "manifest.json", {
        "scope": "development-only, finite prior, fixed two-experiment sequence",
        "seed": 20260920, "episodes": 12, "requests_per_provider": 25,
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "authorized_total_budget_usd": 10.0, "initial_stage_budget_usd": 1.0,
        "jev_reserve_per_request_usd": RESERVE, "jev_model": MODEL, "endpoint": ENDPOINT,
        "offline_task_gate": gate, "round1_weak_episodes": weak,
        "round2_strong_episodes": strong, "sha256": {name: sha(out / name) for name in names},
    })
    print(json.dumps({"output": str(out), "offline_task_gate": gate,
                      "round1_weak": weak, "round2_strong": strong}))


def validate_distribution(answer):
    if answer.get("type") != "choice" or set(answer.get("probabilities", {})) != set(LABELS):
        raise ValueError("wrong answer type or probability labels")
    values = [answer["probabilities"][label] for label in LABELS]
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or
           not math.isfinite(v) or v < 0 or v > 1 for v in values):
        raise ValueError("invalid probability value")
    if abs(sum(values) - 1) > 1e-6:
        raise ValueError("probabilities do not sum to one")
    if answer.get("choice") not in LABELS or answer["probabilities"][answer["choice"]] < max(values) - 1e-6:
        raise ValueError("choice disagrees with probabilities")
    return values


def payload(case):
    return {"model": MODEL, "state": case["state"], "questions": {
        "mechanism": {"type": "choice", "instructions": INSTRUCTIONS, "criteria": CRITERIA}}}


def run_jev(out, limit):
    manifest = json.loads((out / "manifest.json").read_text())
    if not manifest["offline_task_gate"]:
        raise SystemExit("Offline task gate failed; no request sent.")
    for name, expected in manifest["sha256"].items():
        if sha(out / name) != expected:
            raise SystemExit(f"Frozen artifact changed: {name}")
    if sha(Path(__file__)) != sha(out / "sources/drag_pilot.py"):
        raise SystemExit("Runner differs from frozen source; no request sent.")
    key = load_key("openrouter")
    if not key:
        raise SystemExit("OpenRouter key missing; configure it in your terminal.")
    with (out / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        pending = out / "pending.json"
        if pending.exists():
            raise SystemExit("Uncertain earlier request; reconcile pending.json before continuing.")
        ledger_path = out / "api_ledger.jsonl"
        ledger = read_lines(ledger_path)
        if any(row["status"] != "valid" for row in ledger):
            raise SystemExit("An earlier attempt failed; inspect it before a new batch.")
        charged = sum(r["budget_charge_usd"] for r in ledger)
        done = {r["case_id"] for r in ledger if r["provider"] == "openrouter-jev"}
        cases = [c for c in read_lines(out / "requests.jsonl") if c["id"] not in done][:limit]
        for case in cases:
            if charged + RESERVE > min(1.0, manifest["initial_stage_budget_usd"]):
                raise SystemExit("Initial-stage budget limit reached.")
            body = payload(case)
            encoded = json.dumps(body, allow_nan=False).encode()
            if len(encoded) > 20000:
                raise SystemExit("Request exceeds the reserved size envelope.")
            row = {"case_id": case["id"], "provider": "openrouter-jev",
                   "requested_model": MODEL, "endpoint": ENDPOINT,
                   "reserve_usd": RESERVE, "request": body}
            write_json(pending, row)
            started = time.monotonic()
            try:
                req = urllib.request.Request(ENDPOINT, data=encoded, headers={
                    "Authorization": "Bearer " + key, "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=45) as response:
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
                    row.update(returned_model=obj.get("model"), returned_provider=obj.get("provider"),
                               response_id=obj.get("id"), usage=obj.get("usage"))
                    row["probabilities"] = validate_distribution(obj["answers"]["mechanism"])
                    if obj.get("model") not in {MODEL, "jev-1.13", "jev-1.13.0",
                                               "typesafe/jev-1.13.0", "typesafe/jev-1.13-20260917"}:
                        raise ValueError("response does not identify the pinned Jev version")
                    row["status"] = "valid"
                except (ValueError, KeyError, TypeError) as error:
                    row.update(status="invalid_response", error_type=type(error).__name__)
            row["elapsed_seconds"] = time.monotonic() - started
            cost = (row.get("usage") or {}).get("cost")
            if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0:
                cost = None
            row["reported_cost_usd"] = cost
            row["budget_charge_usd"] = max(RESERVE, cost or 0)
            append(ledger_path, row)
            charged += row["budget_charge_usd"]
            if row["status"] != "transport_uncertain":
                pending.unlink()
            print(json.dumps({k: row[k] for k in ("case_id", "status", "reported_cost_usd", "budget_charge_usd")}))
            if row["status"] != "valid" or (cost is not None and cost > RESERVE):
                raise SystemExit("Stopped after unexpected response or cost; no automatic retry.")


def retained(p):
    order = sorted(range(3), key=lambda i: (-p[i], i))
    keep, mass = [], 0.0
    for i in order:
        keep.append(i)
        mass += p[i]
        if mass >= 0.95 - 1e-12:
            break
    return keep


def score(p, ref):
    p = np.asarray(p)
    oracle = np.asarray(ref["posterior"])
    result = {"tv": float(np.abs(p - oracle).sum() / 2)}
    if ref["truth"] is None:
        return result
    y = LABELS.index(ref["truth"])
    result.update(brier=float(np.sum((p - np.eye(3)[y]) ** 2)),
                  log_loss=float(-np.log(max(p[y], 1e-12))),
                  zero_true_probability=bool(p[y] == 0), correct=bool(np.argmax(p) == y),
                  retained_size=len(retained(p)), excluded=bool(y not in retained(p)),
                  confident=bool(max(p) >= 0.95),
                  confident_wrong=bool(max(p) >= 0.95 and np.argmax(p) != y))
    return result


def summarize(out):
    truth = {r["id"]: r for r in read_lines(out / "reference.jsonl")}
    ledger = read_lines(out / "api_ledger.jsonl")
    metrics = []
    for name in ("reference", "uniform", "jev"):
        entries = ([{"case_id": r["id"], "probabilities": r["posterior"] if name == "reference" else [1/3]*3}
                    for r in truth.values()] if name != "jev" else
                   [r for r in ledger if r["status"] == "valid" and r["provider"] == "openrouter-jev"])
        for row in entries:
            ref = truth[row["case_id"]]
            metrics.append({"method": name, "case_id": row["case_id"],
                            "episode": ref["episode"], "round": ref["round"],
                            **score(row["probabilities"], ref)})
    write_json(out / "metrics.json", metrics)
    lines = ["# Drag mechanism development results", "",
             "Development cases only. No OpenAI or Anthropic comparison has been run by this runner.", "",
             "| Method | Round | n | Accuracy | Brier | Mean TV | Excluded true law | Confident wrong |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for name, round_id in itertools.product(("reference", "uniform", "jev"), (1, 2)):
        group = [m for m in metrics if m["method"] == name and m["round"] == round_id]
        if group:
            mean = lambda k: float(np.mean([m[k] for m in group]))
            lines.append(f"| {name} | {round_id} | {len(group)} | {mean('correct'):.3f} | "
                         f"{mean('brier'):.4f} | {mean('tv'):.4f} | "
                         f"{sum(m['excluded'] for m in group)} | {sum(m['confident_wrong'] for m in group)} |")
    jev = [m for m in metrics if m["method"] == "jev" and m["round"] > 0]
    if len(jev) == 24:
        bad = {m["episode"] for m in jev if m["confident_wrong"]}
        excluded = {m["episode"] for m in jev if m["excluded"]}
        first_crossing = {}
        for m in sorted(jev, key=lambda x: x["round"]):
            if m["confident"]:
                first_crossing.setdefault(m["episode"], m)
        passed = (np.mean([m["brier"] for m in jev if m["round"] == 2]) <= 2/3 - 0.05
                  and np.median([m["tv"] for m in jev]) <= 0.20 and len(bad) <= 1)
        lines += ["", f"Jev development heuristic: {'pass' if passed else 'fail'}.",
                  f"Episodes with any exclusion of the true law: {len(excluded)}/12.",
                  f"Episodes with any confident wrong choice: {len(bad)}/12.",
                  f"Confident wrong at first crossing: {sum(m['confident_wrong'] for m in first_crossing.values())}/{len(first_crossing)}.",
                  "The three-model screen remains incomplete until both LLM baselines are evaluated."]
    else:
        lines += ["", f"Jev task responses completed: {len(jev)}/24. This partial run does not provide the complete development comparison."]
    control = [m for m in metrics if m["method"] == "jev" and m["round"] == 0]
    if control:
        lines += [f"Empty-data control TV: {control[0]['tv']:.4f}."]
    lines += ["", f"API attempts: {len(ledger)}.",
              f"Conservative budget charge: USD {sum(r['budget_charge_usd'] for r in ledger):.4f}.",
              f"Reported cost (known entries only): USD {sum(r['reported_cost_usd'] or 0 for r in ledger):.8f}.",
              f"Attempts with unknown billed cost: {sum(r['reported_cost_usd'] is None for r in ledger)}."]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run-jev", "summarize"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=1)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    if args.command == "prepare":
        prepare(args.output)
    elif args.command == "run-jev":
        run_jev(args.output, args.limit)
    else:
        summarize(args.output)


if __name__ == "__main__":
    main()
