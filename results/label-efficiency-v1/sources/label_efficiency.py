"""Total-label, per-action selective-risk diagnostic. No network or model calls."""

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import shutil

import numpy as np
import scipy
from scipy.stats import beta, t
import sklearn
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from offline_pilot import BITS, certificate_bound, error_distribution, make_world, program, sample

ROOT = Path(__file__).resolve().parents[1]
CONFIG = dict(seed=20260921, repeats=20, budgets=[1024, 2048, 4096, 8192],
              alpha=.05, delta=.05, n_thresholds=21,
              regimes=["honest", "overconfident", "saturated"])
METHODS = ("uniform_full", "graph_certificate_full", "graph_independent_full",
           "graph_certificate_matched", "graph_independent_matched", "e2e_hgb",
           "e2e_logistic", "e2e_cell", "graph_hgb", "oracle_observable")
RAW_LEARNERS = ("e2e_hgb", "e2e_logistic", "e2e_cell")
LEARNERS = RAW_LEARNERS + ("graph_hgb",)


def observed_world(name, mechanism, regime):
    latent = make_world(name, mechanism)
    confidence = latent["q"].copy()
    if regime == "overconfident":
        confidence = 1 - .1 * (1 - confidence)
    elif regime == "saturated":
        confidence[:] = .999
    elif regime != "honest":
        raise ValueError(regime)
    bits, actions = latent["bits"], latent["actions"]
    reported_p = np.where(bits, confidence, 1 - confidence)
    features = np.column_stack((reported_p, bits, confidence, actions))
    _, cell_ids = np.unique(features, axis=0, return_inverse=True)
    counts = np.bincount(cell_ids)
    conditional_risk = np.bincount(cell_ids, weights=latent["risk"]) / counts
    certificate = np.array([certificate_bound(b, q, name) for b, q in zip(bits, confidence)])
    independent = np.array([error_distribution(q, "independent") @
                            (program(b ^ BITS, name) != action)
                            for b, q, action in zip(bits, confidence, actions)])
    sensitivity = np.column_stack([program(bits ^ np.eye(3, dtype=int)[i], name) != actions
                                   for i in range(3)])
    graph_features = np.column_stack((features, certificate, independent, sensitivity))
    fixed = dict(uniform_full=1-confidence.min(axis=1),
                 graph_certificate_full=certificate, graph_independent_full=independent,
                 graph_certificate_matched=certificate, graph_independent_matched=independent,
                 oracle_observable=conditional_risk[cell_ids])
    return dict(latent=latent, features=features, graph_features=graph_features,
                cell_ids=cell_ids, actions=actions, risk=latent["risk"], fixed=fixed)


def fitted_scores(world, ids, errors, repeat):
    """Learners see observable features and terminal labels, never latent q."""
    cells = world["cell_ids"]
    count = np.bincount(cells[ids], minlength=cells.max()+1)
    wrong = np.bincount(cells[ids], weights=errors, minlength=len(count))
    cell_score = ((wrong + 5 * errors.mean()) / (count + 5))[cells]
    scores = dict(e2e_cell=cell_score)
    for name in ("e2e_hgb", "e2e_logistic", "graph_hgb"):
        features = world["graph_features"] if name == "graph_hgb" else world["features"]
        if len(np.unique(errors)) == 1:
            scores[name] = np.full(len(features), float(errors[0]))
            continue
        if name == "e2e_logistic":
            model = make_pipeline(PolynomialFeatures(2, include_bias=False), StandardScaler(),
                                  LogisticRegression(C=1, max_iter=2000, random_state=repeat))
        else:
            model = HistGradientBoostingClassifier(max_iter=150, max_leaf_nodes=15,
                    min_samples_leaf=20, l2_regularization=1, early_stopping=False,
                    random_state=repeat)
        model.fit(features[ids], errors)
        scores[name] = model.predict_proba(features)[:, 1]
    return scores


def tail_probability(config):
    return config["delta"] / (len(METHODS) * 2 * config["n_thresholds"] * len(config["budgets"]))


def certify(score, actions, ids, errors, config):
    selections = {}
    for action in (0, 1):
        thresholds = np.quantile(score[actions == action], np.linspace(0, 1, config["n_thresholds"]))
        accepted = ((score[ids, None] <= thresholds[None, :]) &
                    (actions[ids, None] == action))
        n = accepted.sum(axis=0)
        m = (accepted * errors[:, None]).sum(axis=0)
        upper = np.ones(len(thresholds))
        valid = (n > 0) & (m < n)
        upper[valid] = beta.ppf(1-tail_probability(config), m[valid]+1, n[valid]-m[valid])
        candidates = np.flatnonzero((n > 0) & (upper <= config["alpha"]))
        if not len(candidates):
            selections[str(action)] = dict(threshold=None, cal_accepted=0, cal_errors=0,
                                            cal_upper=None, status="no_certified_policy")
        else:
            j = min(candidates, key=lambda j: (-n[j], upper[j], thresholds[j]))
            selections[str(action)] = dict(threshold=float(thresholds[j]),
                cal_accepted=int(n[j]), cal_errors=int(m[j]), cal_upper=float(upper[j]),
                status="certified")
    return selections


def evaluate(score, world, selections):
    mask = np.zeros(len(score), dtype=bool)
    groups = {}
    for action in (0, 1):
        group = world["actions"] == action
        selected = selections[str(action)]
        kept = group & (score <= selected["threshold"]) if selected["threshold"] is not None else np.zeros_like(group)
        mask |= kept
        groups[str(action)] = dict(**selected, automation=float(kept.sum()/group.sum()),
            population_mass=float(kept.mean()), risk=float(world["risk"][kept].mean()) if kept.any() else None)
    return dict(automation=float(mask.mean()),
        balanced_automation=min(g["automation"] for g in groups.values()),
        pooled_risk=float(world["risk"][mask].mean()) if mask.any() else None,
        groups=groups)


def paired_interval(values):
    values = np.asarray(values)
    mean = float(values.mean())
    if len(values) < 2:
        return dict(mean=mean, lower=None, upper=None)
    half = float(t.ppf(.975, len(values)-1) * values.std(ddof=1) / np.sqrt(len(values)))
    return dict(mean=mean, lower=mean-half, upper=mean+half)


def analyze(records, config):
    groups = {}
    for row in records:
        key = (row["program"], row["mechanism"], row["regime"], row["budget"], row["method"])
        groups.setdefault(key, []).append(row)
    aggregate = []
    means = {}
    for key, rows in groups.items():
        risks = [g["risk"] for r in rows for g in r["groups"].values() if g["risk"] is not None]
        avg = float(np.mean([r["balanced_automation"] for r in rows]))
        means[key] = avg
        aggregate.append(dict(zip(("program", "mechanism", "regime", "budget", "method"), key),
            mean_automation=float(np.mean([r["automation"] for r in rows])),
            mean_balanced_automation=avg, max_action_risk=max(risks) if risks else None,
            action_risk_violations=sum(r > config["alpha"] + 1e-12 for r in risks),
            both_actions_certified=sum(all(g["risk"] is not None for g in r["groups"].values()) for r in rows)))
    comparisons = []
    for mechanism, budget in itertools.product(("independent", "shared"), (2048, 4096)):
        prefix = ("routed", mechanism, "overconfident", budget)
        graph_rows = sorted(groups[prefix+("graph_hgb",)], key=lambda r: r["repeat"])
        graph_mean = means[prefix+("graph_hgb",)]
        differences = {}
        for method in RAW_LEARNERS:
            baseline = sorted(groups[prefix+(method,)], key=lambda r: r["repeat"])
            differences[method] = paired_interval([a["balanced_automation"]-b["balanced_automation"]
                                                   for a, b in zip(graph_rows, baseline)])
        oracle_mean = means[prefix+("oracle_observable",)]
        informative = oracle_mean >= .10
        passed = informative and graph_mean >= .10 and all(
            d["mean"] >= .05 and d["lower"] is not None and d["lower"] > 0 for d in differences.values())
        comparisons.append(dict(mechanism=mechanism, budget=budget, graph_mean=graph_mean,
            best_baseline_mean=max(means[prefix+(m,)] for m in RAW_LEARNERS),
            oracle_mean=oracle_mean, differences=differences,
            status="pass" if passed else "fail" if informative else "uninformative"))
    passed_budgets = [b for b in (2048, 4096) if all(
        r["status"] == "pass" for r in comparisons if r["budget"] == b)]
    informative_budget = any(all(r["status"] != "uninformative" for r in comparisons if r["budget"] == b)
                             for b in (2048, 4096))
    reached = []
    for name, mechanism, regime, method in itertools.product(
            ("all_required", "routed"), ("independent", "shared"), config["regimes"], METHODS):
        qualifying = [b for b in config["budgets"] if means[(name, mechanism, regime, b, method)] >= .10]
        reached.append(dict(program=name, mechanism=mechanism, regime=regime, method=method,
                            first_tested_budget_at_10_percent=min(qualifying) if qualifying else None))
    return dict(screen_status="pass" if passed_budgets else "fail" if informative_budget else "uninformative",
                passed_budgets=passed_budgets, primary_comparisons=comparisons,
                aggregates=aggregate, first_budgets=reached)


def write_summary(out, analysis, config):
    lines = ["# Total-label diagnostic", "", f"Exploratory mechanism screen: **{analysis['screen_status']}**.", "",
        f"{config['repeats']} repeats; per-action selective-risk target .05; no API calls.",
        "Exact population evaluation. The reference sees observable inputs only.", "",
        "| Routed errors / overconfident scores | Total labels | Graph HGB balanced automation | Best raw learner | Observable oracle | Screen |",
        "|---|---:|---:|---:|---:|---|"]
    for row in analysis["primary_comparisons"]:
        lines.append(f"| {row['mechanism']} | {row['budget']} | {row['graph_mean']:.4f} | {row['best_baseline_mean']:.4f} | {row['oracle_mean']:.4f} | {row['status']} |")
    lines += ["", "Paired differences are graph HGB minus the specified raw learner. Intervals describe",
              "Monte Carlo uncertainty; they are not multiplicity-adjusted confirmatory intervals.", "",
              "| Errors | Budget | Raw learner | Mean difference | Paired 95% interval |",
              "|---|---:|---|---:|---|"]
    for row in analysis["primary_comparisons"]:
        for method, diff in row["differences"].items():
            interval = "undefined" if diff["lower"] is None else f"[{diff['lower']:.4f}, {diff['upper']:.4f}]"
            lines.append(f"| {row['mechanism']} | {row['budget']} | {method} | {diff['mean']:.4f} | {interval} |")
    violations = sum(r["action_risk_violations"] for r in analysis["aggregates"])
    need = math.ceil(math.log(tail_probability(config))/math.log(1-config["alpha"]))
    lines += ["", f"Observed action-risk violations: {violations}. Zero-error accepted labels needed per candidate: {need}.",
        "A small number of simulation repeats cannot validate the theoretical confidence level.", "",
        "## Full results", "", "| Program | Errors | Scores | Budget | Method | Automation | Balanced automation | Max action risk |",
        "|---|---|---|---:|---|---:|---:|---:|"]
    for row in analysis["aggregates"]:
        risk = "undefined" if row["max_action_risk"] is None else f"{row['max_action_risk']:.4f}"
        lines.append(f"| {row['program']} | {row['mechanism']} | {row['regime']} | {row['budget']} | {row['method']} | {row['mean_automation']:.4f} | {row['mean_balanced_automation']:.4f} | {risk} |")
    lines += ["", "All thresholds, accepted counts, and action risks are in `runs.jsonl`. `analysis.json`",
        "includes the first tested budget reaching 10% balanced automation (null means not reached).",
        "Population arrays, score vectors, and fit/calibration pools are retained in compressed NPZ files.",
        "The screen is a resource decision for these candidates, not a novelty test or a result about Jev."]
    (out/"summary.md").write_text("\n".join(lines)+"\n")


def plot(out, analysis):
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True, sharey=True)
    methods = ("graph_independent_full", "graph_independent_matched", "e2e_hgb",
               "e2e_logistic", "e2e_cell", "graph_hgb", "oracle_observable")
    for ax, (mechanism, regime) in zip(axes.flat, itertools.product(("independent", "shared"), CONFIG["regimes"])):
        for method in methods:
            rows = sorted([r for r in analysis["aggregates"] if
                (r["program"], r["mechanism"], r["regime"], r["method"]) == ("routed", mechanism, regime, method)],
                key=lambda r: r["budget"])
            ax.plot([r["budget"] for r in rows], [r["mean_balanced_automation"] for r in rows],
                    marker="o", markersize=3, label=method, linestyle="--" if method == "oracle_observable" else "-")
        ax.axhline(.10, color="grey", alpha=.4, linewidth=.8)
        ax.set_title(f"{mechanism} / {regime}")
        ax.set_xscale("log", base=2)
        ax.set_xticks(CONFIG["budgets"], CONFIG["budgets"])
        ax.set_ylim(-.02, 1.02)
        ax.grid(alpha=.15)
    for ax in axes[-1]:
        ax.set_xlabel("Total terminal-error labels")
    for ax in axes[:, 0]:
        ax.set_ylabel("Mean balanced automation")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8)
    fig.suptitle("Routed workflow: per-action risk control at 5%\nBalanced automation = minimum of approve and deny automation", fontsize=12)
    fig.tight_layout(rect=(0, .09, 1, .91))
    fig.savefig(out/"label_curves.png", dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=CONFIG["repeats"])
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("repeats must be positive")
    out = args.output
    out.mkdir(parents=True, exist_ok=False)
    config = dict(CONFIG, repeats=args.repeats)
    sources = [Path(__file__), ROOT/"scripts/offline_pilot.py"]
    snapshots = out/"sources"
    snapshots.mkdir()
    for p in sources:
        shutil.copyfile(p, snapshots/p.name)
    manifest = dict(config=config, methods=METHODS, started_utc=datetime.now(timezone.utc).isoformat(),
        versions=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, sklearn=sklearn.__version__),
        source_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        tail_probability=tail_probability(config),
        zero_error_accepted_needed=math.ceil(math.log(tail_probability(config))/math.log(1-config["alpha"])))
    (out/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    records = []
    pool_n = max(config["budgets"])//2
    with (out/"runs.jsonl").open("w") as stream:
        for gi, name in enumerate(("all_required", "routed")):
            for mi, mechanism in enumerate(("independent", "shared")):
                for regime in config["regimes"]:
                    world = observed_world(name, mechanism, regime)
                    prefix = f"{name}-{mechanism}-{regime}"
                    np.savez_compressed(out/f"{prefix}-population.npz", features=world["features"],
                        graph_features=world["graph_features"], latent_q=world["latent"]["q"],
                        actions=world["actions"], risk=world["risk"], cell_ids=world["cell_ids"])
                    scores_saved, pools = [], []
                    for repeat in range(config["repeats"]):
                        fit_rng = np.random.default_rng(np.random.SeedSequence([config["seed"], gi, mi, repeat, 0]))
                        cal_rng = np.random.default_rng(np.random.SeedSequence([config["seed"], gi, mi, repeat, 1]))
                        fit_ids, fit_errors = sample(world["latent"], pool_n, fit_rng)
                        cal_ids, cal_errors = sample(world["latent"], pool_n, cal_rng)
                        pools.append(np.stack((fit_ids, fit_errors, cal_ids, cal_errors)))
                        for budget in config["budgets"]:
                            n = budget//2
                            scores = dict(world["fixed"], **fitted_scores(world, fit_ids[:n], fit_errors[:n], repeat))
                            scores_saved.append(np.array([scores[m] for m in METHODS]))
                            for method in METHODS:
                                full = method.endswith("_full") or method == "oracle_observable"
                                ids = np.concatenate((fit_ids[:n], cal_ids[:n])) if full else cal_ids[:n]
                                errors = np.concatenate((fit_errors[:n], cal_errors[:n])) if full else cal_errors[:n]
                                selected = certify(scores[method], world["actions"], ids, errors, config)
                                row = dict(program=name, mechanism=mechanism, regime=regime,
                                    repeat=repeat, budget=budget, method=method,
                                    fit_labels=n if method in LEARNERS else 0,
                                    calibration_labels=len(ids), unused_labels=n if method.endswith("_matched") else 0,
                                    **evaluate(scores[method], world, selected))
                                records.append(row)
                                stream.write(json.dumps(row, allow_nan=False)+"\n")
                    stream.flush()
                    np.savez_compressed(out/f"{prefix}-samples-scores.npz", pools=np.array(pools),
                        scores=np.array(scores_saved).reshape(config["repeats"], len(config["budgets"]), len(METHODS), -1))
                    print(f"Finished {prefix}", flush=True)
    analysis = analyze(records, config)
    (out/"analysis.json").write_text(json.dumps(analysis, indent=2, allow_nan=False)+"\n")
    write_summary(out, analysis, config)
    plot(out, analysis)
    hashes = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(out.rglob("*")) if p.is_file()}
    (out/"artifact_hashes.json").write_text(json.dumps(hashes, indent=2)+"\n")
    print(f"Screen: {analysis['screen_status']}; results: {out}", flush=True)


if __name__ == "__main__":
    main()
