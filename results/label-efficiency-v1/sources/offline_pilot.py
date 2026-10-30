"""Finite-population diagnostics for selective execution. No model API calls."""

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.stats import beta
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path(__file__).resolve().parents[1]
CONFIG = dict(seed=20260920, repeats=20, train_sizes=[512, 4096], n_cal=4000,
              alpha=0.05, delta=0.05, n_thresholds=21, q_levels=[0.55, 0.8, 0.98])
METHODS = ("uniform", "all_nodes_product", "graph_certificate", "graph_independent",
           "e2e_hgb", "oracle_terminal")
BITS = np.array(list(itertools.product((0, 1), repeat=3)), dtype=int)


def program(bits, name):
    if name == "all_required":
        return np.all(bits, axis=-1).astype(int)
    if name == "routed":
        return np.where(bits[..., 0], bits[..., 1], bits[..., 2])
    raise ValueError(name)


def upper_bound(errors, accepted, tail):
    if accepted == 0 or errors == accepted:
        return 1.0
    return float(beta.ppf(1 - tail, errors + 1, accepted - errors))


def error_distribution(q, mechanism):
    e = 1 - np.asarray(q)
    if mechanism == "independent":
        return np.prod(np.where(BITS, e, 1 - e), axis=1)
    if mechanism == "shared":
        lower = np.max(np.where(BITS == 0, e, 0.0), axis=1)
        upper = np.min(np.where(BITS == 1, e, 1.0), axis=1)
        return np.maximum(0.0, upper - lower)
    raise ValueError(mechanism)


def certificate_bound(bits, q, name):
    """Smallest union bound among subsets fixing the predicted terminal action."""
    action = program(bits, name)
    best = 1.0
    for fixed in BITS.astype(bool):
        possible = BITS[np.all(BITS[:, fixed] == bits[fixed], axis=1)]
        if np.all(program(possible, name) == action):
            best = min(best, float(np.sum((1 - q)[fixed])))
    return best


def make_world(name, mechanism):
    rows = [(b, q) for b in BITS for q in itertools.product(CONFIG["q_levels"], repeat=3)]
    bits = np.array([b for b, q in rows])
    q = np.array([q for b, q in rows])
    p = np.where(bits, q, 1 - q)
    actions = program(bits, name)
    risk = np.array([np.sum(error_distribution(qi, mechanism) *
                            (program(bi ^ BITS, name) != ai))
                     for bi, qi, ai in zip(bits, q, actions)])
    features = np.column_stack((p, bits, q, actions))
    return dict(bits=bits, q=q, p=p, actions=actions, risk=risk, features=features,
                name=name, mechanism=mechanism)


def sample(world, n, rng):
    indices = rng.integers(len(world["q"]), size=n)
    width = 3 if world["mechanism"] == "independent" else 1
    errors = rng.random((n, width)) < (1 - world["q"][indices])
    labels = world["bits"][indices] ^ errors
    terminal_errors = program(labels, world["name"]) != world["actions"][indices]
    return indices, terminal_errors.astype(int)


def choose(score, cal_ids, cal_errors, config):
    thresholds = np.quantile(score, np.linspace(0, 1, config["n_thresholds"]))
    tail = config["delta"] / (len(METHODS) * config["n_thresholds"])
    candidates = []
    for threshold in thresholds:
        accepted = score[cal_ids] <= threshold
        n, m = int(accepted.sum()), int(cal_errors[accepted].sum())
        upper = upper_bound(m, n, tail)
        if n and upper <= config["alpha"]:
            candidates.append(dict(threshold=float(threshold), cal_accepted=n,
                                   cal_errors=m, cal_upper=upper))
    if not candidates:
        return dict(threshold=None, cal_accepted=0, cal_errors=0, cal_upper=None,
                    status="no_certified_policy")
    selected = sorted(candidates, key=lambda r: (-r["cal_accepted"], r["cal_upper"],
                                                r["threshold"]))[0]
    return dict(selected, status="certified")


def evaluate(score, selected, world, shifted):
    mask = np.zeros(len(score), dtype=bool) if selected["threshold"] is None else score <= selected["threshold"]
    risk = float(world["risk"][mask].mean()) if mask.any() else None
    by_action = {}
    for action in (0, 1):
        group = world["actions"] == action
        kept = mask & group
        by_action[str(action)] = dict(coverage=float(mask[group].mean()),
                                      risk=float(world["risk"][kept].mean()) if kept.any() else None)
    return dict(coverage=float(mask.mean()), true_risk=risk, by_predicted_action=by_action,
                shifted_risk=float(shifted["risk"][mask].mean()) if mask.any() else None)


def exact_checks():
    even = np.array([0.25 if b.sum() % 2 == 0 else 0 for b in BITS])
    odd = 0.25 - even
    # Each bit has marginal .5, and each pair has joint error probability .25.
    assert np.allclose(even @ BITS, odd @ BITS)
    for i, j in itertools.combinations(range(3), 2):
        assert np.isclose(even @ (BITS[:, i] * BITS[:, j]), odd @ (BITS[:, i] * BITS[:, j]))
    tail = CONFIG["delta"] / (len(METHODS) * CONFIG["n_thresholds"])
    return dict(three_nodes_95_percent=dict(independent=0.95**3, coincident=0.95,
                                           mutually_exclusive=0.85),
                pairwise_nonidentification=dict(marginals=[0.5]*3, pairwise_joint_error=[0.25]*3,
                                               p_no_error_even=float(even[0]), p_no_error_odd=float(odd[0])),
                zero_error_accepted_needed=math.ceil(math.log(tail)/math.log(1-CONFIG["alpha"])),
                marginal_coverage_not_selective=dict(set_coverage=0.95, singleton_rate=0.05,
                                                      singleton_error_rate=1.0))


def write_summary(out, records, config):
    lines = ["# Offline pilot", "", "Exploratory finite synthetic population; no LLM or Jev calls.", "",
             f"{config['repeats']} independent development/calibration repeats per condition; "
             f"{config['n_cal']} calibration episodes; alpha={config['alpha']}, delta={config['delta']}.",
             "Population coverage and risk are enumerated exactly. Below, coverage is averaged across repeats; "
             "risk is the maximum among certified repeats. No-policy outcomes have coverage zero and undefined risk.", "",
             "| Program | Errors | Dev labels | Method | Mean coverage | Max risk | Certified | Risk violations | Shift violations |",
             "|---|---|---:|---|---:|---:|---:|---:|---:|"]
    for name, mechanism, n in itertools.product(("all_required", "routed"), ("independent", "shared"), config["train_sizes"]):
        for method in METHODS:
            group = [r for r in records if (r["program"], r["mechanism"], r["n_train"], r["method"]) == (name, mechanism, n, method)]
            risks = [r["true_risk"] for r in group if r["true_risk"] is not None]
            max_risk = f"{max(risks):.4f}" if risks else "undefined"
            violations = sum(r > config["alpha"] + 1e-12 for r in risks)
            shift = sum(r["shifted_risk"] is not None and r["shifted_risk"] > config["alpha"] + 1e-12 for r in group)
            lines.append(f"| {name} | {mechanism} | {n} | {method} | {np.mean([r['coverage'] for r in group]):.4f} | {max_risk} | {len(risks)}/{len(group)} | {violations} | {shift} |")
    lines += ["", "The oracle has access to the true terminal error distribution. The independent graph score "
              "is itself the oracle score under independent errors. Neither establishes a new algorithm.", "",
              "Graph scores receive exact conditional node probabilities in this experiment. Real API scores "
              "do not satisfy that assumption by construction. Shift columns change the error dependence after "
              "calibration and are outside the guarantee. No errors in 20 repeats do not validate a 95% guarantee.", "",
              "Per-action coverage/risk, candidate selections, and every repeat are retained in `runs.jsonl`."]
    (out / "summary.md").write_text("\n".join(lines) + "\n")


def plot(out, records, config):
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharey=True)
    colors = ["#999999", "#b6b6b6", "#197a78", "#d17d29", "#4555a5", "#262626"]
    for ax, (name, mechanism) in zip(axes.flat, itertools.product(("all_required", "routed"), ("independent", "shared"))):
        for mi, method in enumerate(METHODS):
            means, spreads = [], []
            for n in config["train_sizes"]:
                vals = [r["coverage"] for r in records if (r["program"], r["mechanism"], r["n_train"], r["method"]) == (name, mechanism, n, method)]
                means.append(np.mean(vals)); spreads.append(np.std(vals, ddof=1) if len(vals)>1 else 0)
            x = np.arange(len(means)) + (mi - 2.5) * 0.12
            ax.errorbar(x, means, yerr=spreads, fmt="o", color=colors[mi], label=method, capsize=2, markersize=4)
        ax.set_title(f"{name} / {mechanism} errors")
        ax.set_xticks(range(len(config["train_sizes"])), config["train_sizes"])
        ax.set_xlabel("Development labels")
        ax.set_ylim(-0.03, 1.04)
        ax.grid(axis="y", alpha=0.2)
    axes[0, 0].set_ylabel("Exact population automation rate")
    axes[1, 0].set_ylabel("Exact population automation rate")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=9)
    fig.suptitle("Synthetic diagnostic: certified automation at 5% selective risk\nPoints: mean; bars: between-repeat SD (not confidence intervals)", fontsize=12)
    fig.tight_layout(rect=(0, 0.09, 1, 0.92))
    fig.savefig(out / "coverage.png", dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=CONFIG["repeats"])
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    config = dict(CONFIG, repeats=args.repeats)
    manifest = dict(config=config, started_utc=datetime.now(timezone.utc).isoformat(),
                    versions=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, sklearn=sklearn.__version__),
                    source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in (Path(__file__),)})
    (out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    (out/"mechanisms.json").write_text(json.dumps(exact_checks(), indent=2)+"\n")
    records = []
    with (out/"runs.jsonl").open("w") as stream:
        for gi, name in enumerate(("all_required", "routed")):
            for di, mechanism in enumerate(("independent", "shared")):
                world = make_world(name, mechanism)
                shifted = make_world(name, "shared" if mechanism == "independent" else "independent")
                independent = make_world(name, "independent")
                fixed = dict(uniform=1-world["q"].min(axis=1),
                             all_nodes_product=1-world["q"].prod(axis=1),
                             graph_certificate=np.array([certificate_bound(b, q, name) for b, q in zip(world["bits"], world["q"])]),
                             graph_independent=independent["risk"], oracle_terminal=world["risk"])
                for repeat in range(config["repeats"]):
                    dev_rng = np.random.default_rng(np.random.SeedSequence([config["seed"], gi, di, repeat, 0]))
                    cal_rng = np.random.default_rng(np.random.SeedSequence([config["seed"], gi, di, repeat, 1]))
                    dev_ids, dev_errors = sample(world, max(config["train_sizes"]), dev_rng)
                    cal_ids, cal_errors = sample(world, config["n_cal"], cal_rng)
                    for n in config["train_sizes"]:
                        model = HistGradientBoostingClassifier(max_iter=150, max_leaf_nodes=15, min_samples_leaf=20,
                                                               l2_regularization=1.0, early_stopping=False, random_state=repeat)
                        model.fit(world["features"][dev_ids[:n]], dev_errors[:n])
                        scores = dict(fixed, e2e_hgb=model.predict_proba(world["features"])[:, 1])
                        for method in METHODS:
                            selected = choose(scores[method], cal_ids, cal_errors, config)
                            row = dict(program=name, mechanism=mechanism, repeat=repeat, n_train=n, method=method,
                                       **selected, **evaluate(scores[method], selected, world, shifted))
                            records.append(row)
                            stream.write(json.dumps(row, allow_nan=False)+"\n")
                    stream.flush()
                print(f"Finished {name}/{mechanism}", flush=True)
    write_summary(out, records, config)
    plot(out, records, config)
    print(f"Results: {out}")


if __name__ == "__main__":
    main()
