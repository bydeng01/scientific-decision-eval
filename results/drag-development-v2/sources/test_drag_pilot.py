import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from scipy.integrate import solve_ivp

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("drag", SCRIPTS / "drag_pilot.py")
drag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drag)


@pytest.mark.parametrize("a,b", [(0.4, 0), (0, 0.4), (0.2, 0.4)])
def test_analytic_solution_against_independent_integrator(a, b):
    times = np.array([0] + drag.TIMES)
    sol = solve_ivp(lambda t, v: -a*v-b*v*np.abs(v), (0, times[-1]), [3.0],
                    t_eval=times, rtol=1e-11, atol=1e-12)
    np.testing.assert_allclose(drag.velocity(times, 3.0, a, b), sol.y[0], rtol=1e-9)


def test_marginalization_uses_shared_parameters_and_model_prior():
    # Enumerate all latent states independently of the log-space implementation.
    cases, refs = drag.generate()
    for index in (0, 2, 8, 24):
        experiments = cases[index]["state"]["experiments"]
        masses = []
        for label in drag.LABELS:
            marginal = 0.0
            for a, b in drag.PARAMS[label]:
                likelihood = 1.0
                for exp in experiments:
                    pred = drag.velocity(exp["times"], exp["initial_velocity"], a, b)
                    errors = (np.array(exp["observed_velocity"])-pred)/drag.SIGMA
                    likelihood *= np.exp(-0.5 * errors @ errors)
                marginal += likelihood / len(drag.PARAMS[label]) / 3
            masses.append(marginal)
        np.testing.assert_allclose(np.array(masses)/sum(masses), refs[index]["posterior"], atol=1e-12)


def test_empty_data_gives_equal_model_mass_despite_different_parameter_counts():
    np.testing.assert_allclose(drag.posterior([]), [1/3]*3, atol=1e-12)


def test_model_request_excludes_answer_metadata():
    cases, truth = drag.generate()
    assert len(cases) == len(truth) == 25
    for case in cases:
        body = drag.payload(case)
        assert set(body) == {"model", "state", "questions"}
        for forbidden in ('"posterior":', '"truth":', '"episode":', '"round":', '"id":'):
            assert forbidden not in json.dumps(body)
        assert sum(body["state"]["model_priors"].values()) == 1.0


@pytest.mark.parametrize("values", [[float('nan'), 0, 1], [True, 0, 0], [0.5]*3, [-0.1,0.1,1]])
def test_invalid_probabilities_are_rejected(values):
    with pytest.raises(ValueError):
        drag.validate_distribution({"type": "choice", "choice": "H1",
                                    "probabilities": dict(zip(drag.LABELS, values))})


def test_mass_set_and_wrong_confidence_are_distinct():
    ref = {"truth": "H3", "posterior": [0.4, 0.4, 0.2]}
    assert not drag.score([0.4, 0.4, 0.2], ref)["excluded"]
    assert drag.score([0.96, 0.02, 0.02], ref)["confident_wrong"]


def test_frozen_batch_and_pending_request_stop_before_network(tmp_path, monkeypatch):
    out = tmp_path / "batch"
    drag.prepare(out)
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest["offline_task_gate"]
    monkeypatch.setattr(drag, "load_key", lambda provider: "test-only")
    monkeypatch.setattr(drag.urllib.request, "urlopen", lambda *a, **k: pytest.fail("network called"))
    (out / "pending.json").write_text("{}")
    with pytest.raises(SystemExit, match="Uncertain earlier"):
        drag.run_jev(out, 1)
    (out / "pending.json").unlink()
    with (out / "requests.jsonl").open("a") as f:
        f.write("{}\n")
    with pytest.raises(SystemExit, match="Frozen artifact changed"):
        drag.run_jev(out, 1)
