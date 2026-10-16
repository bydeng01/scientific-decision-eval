import itertools
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from offline_pilot import (BITS, CONFIG, certificate_bound, choose, error_distribution,
                           evaluate, exact_checks, make_world, program, sample, upper_bound)


def test_error_marginals_and_joint_normalization():
    for q in itertools.product(CONFIG["q_levels"], repeat=3):
        for mechanism in ("independent", "shared"):
            masses = error_distribution(q, mechanism)
            assert masses.sum() == pytest.approx(1)
            assert masses.min() >= 0
            assert np.allclose(masses @ BITS, 1-np.array(q))


def test_shared_errors_change_terminal_risk_without_changing_marginals():
    q = np.full(3, .95)
    no_error = np.all(BITS == 0, axis=1)
    assert error_distribution(q, "independent")[no_error].sum() == pytest.approx(.95**3)
    assert error_distribution(q, "shared")[no_error].sum() == pytest.approx(.95)
    checks = exact_checks()["pairwise_nonidentification"]
    assert checks["p_no_error_even"] != checks["p_no_error_odd"]


def test_certificate_ignores_irrelevant_uncertainty_and_bounds_actual_risk():
    assert certificate_bound(np.array([0, 1, 1]), np.array([.98, .55, .55]), "all_required") == pytest.approx(.02)
    for name, mechanism in itertools.product(("all_required", "routed"), ("independent", "shared")):
        w = make_world(name, mechanism)
        bounds = [certificate_bound(b, q, name) for b, q in zip(w["bits"], w["q"])]
        assert np.all(w["risk"] <= np.array(bounds)+1e-12)


def test_binomial_bound_and_no_policy_semantics():
    assert upper_bound(0, 0, .05) == 1
    assert upper_bound(100, 100, .05) == 1
    assert upper_bound(0, 299, .05) == pytest.approx(1-.05**(1/299))
    assert upper_bound(0, 299, .05) < .01
    assert upper_bound(0, 298, .05) > .01
    w = make_world("routed", "shared")
    ids = np.arange(100) % len(w["risk"])
    selected = choose(w["risk"], ids, np.ones(100), CONFIG)
    assert selected["status"] == "no_certified_policy"
    result = evaluate(w["risk"], selected, w, w)
    assert result["coverage"] == 0 and result["true_risk"] is None


def test_generator_matches_exact_population_and_preserves_episodes():
    for mechanism in ("independent", "shared"):
        w = make_world("routed", mechanism)
        _, errors = sample(w, 150000, np.random.default_rng(120))
        assert abs(errors.mean()-w["risk"].mean()) < .004


def test_program_truth_tables():
    assert program(BITS, "all_required").tolist() == [0,0,0,0,0,0,0,1]
    assert program(BITS, "routed").tolist() == [0,1,0,1,0,0,1,1]
