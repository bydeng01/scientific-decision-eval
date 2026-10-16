from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from label_efficiency import CONFIG, certify, evaluate, fitted_scores, observed_world, tail_probability


def test_saturated_observations_do_not_leak_latent_probabilities():
    w = observed_world("routed", "shared", "saturated")
    assert len(np.unique(w["features"], axis=0)) == 8
    ids = np.arange(len(w["risk"]))
    errors = (w["risk"] > .2).astype(int)
    scores = dict(w["fixed"], **fitted_scores(w, ids, errors, 0))
    for cell in np.unique(w["cell_ids"]):
        mask = w["cell_ids"] == cell
        assert np.ptp(w["risk"][mask]) > 0
        for score in scores.values():
            assert np.ptp(score[mask]) < 1e-12
        assert w["fixed"]["oracle_observable"][mask][0] == pytest.approx(w["risk"][mask].mean())


def test_score_distortion_preserves_population_but_changes_scores():
    honest = observed_world("routed", "independent", "honest")
    distorted = observed_world("routed", "independent", "overconfident")
    assert np.array_equal(honest["risk"], distorted["risk"])
    assert np.allclose(honest["fixed"]["graph_independent_full"], honest["risk"])
    assert not np.allclose(distorted["fixed"]["graph_independent_full"], distorted["risk"])
    assert np.allclose(distorted["fixed"]["oracle_observable"], distorted["risk"])


def test_action_specific_certification_does_not_hide_bad_approvals():
    score = np.zeros(2)
    actions = np.array([0, 1])
    ids = np.array([0]*5000 + [1]*1000)
    errors = np.array([0]*5000 + [1]*250 + [0]*750)
    selected = certify(score, actions, ids, errors, CONFIG)
    assert selected["0"]["status"] == "certified"
    assert selected["1"]["status"] == "no_certified_policy"
    w = dict(actions=actions, risk=np.array([0, .25]))
    result = evaluate(score, w, selected)
    assert result["automation"] == .5
    assert result["balanced_automation"] == 0
    assert result["groups"]["1"]["risk"] is None


def test_shared_family_accounts_for_budget_selection():
    assert tail_probability(CONFIG) == pytest.approx(.05/(10*2*21*4))


def test_no_accepted_calibration_cases_cannot_certify():
    selected = certify(np.array([0., 1.]), np.array([0, 1]), np.zeros(1000, dtype=int),
                       np.zeros(1000, dtype=int), CONFIG)
    assert selected["1"]["threshold"] is None


def test_learners_do_not_read_evaluator_risk_or_latent_q():
    w = observed_world("routed", "independent", "honest")
    ids = np.arange(len(w["risk"]))
    errors = (ids % 4 == 0).astype(int)
    before = fitted_scores(w, ids, errors, 0)
    w["risk"] = np.full(len(ids), np.nan)
    w["latent"]["q"][:] = np.nan
    after = fitted_scores(w, ids, errors, 0)
    for name in before:
        assert np.array_equal(before[name], after[name])
