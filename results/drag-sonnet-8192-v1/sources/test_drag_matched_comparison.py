import json
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import drag_matched_comparison as matched
from drag_pilot import append


def test_rounding_keeps_raw_invalid_and_projection_inside_intervals():
    p = [.11, .33, .55]
    with pytest.raises(ValueError, match="sum to one"):
        matched.validate_distribution({"type": "choice", "probabilities": dict(zip(matched.LABELS, p)), "choice": "H3"})
    result = matched.rounding_sensitivity(p, [0, 1, 0])
    assert p == [.11, .33, .55]
    np.testing.assert_allclose(result["derived_probabilities"], np.array(p) + .01/3, atol=1e-12)
    assert result["minimum_tv_to_reference"] == pytest.approx(.665)
    assert p[2] / sum(p) > result["upper"][2]


def test_rounding_bound_can_explain_only_nearby_distributions():
    result = matched.rounding_sensitivity([.11, .26, .63], [1, 0, 0])
    assert result["minimum_tv_to_reference"] == pytest.approx(.885)
    result = matched.rounding_sensitivity([.33, .33, .33], [1/3] * 3)
    assert result["minimum_tv_to_reference"] == pytest.approx(0)
    assert result["reference_inside_rounding_intervals"]
    # Boundary clipping must still give a distribution, without changing zeros.
    result = matched.rounding_sensitivity([1, 0, 0], [1, 0, 0])
    np.testing.assert_allclose(result["derived_probabilities"], [1, 0, 0], atol=1e-12)


@pytest.mark.parametrize("p", [[.2, .2, .2], [.111, .333, .556], [float('nan'), 0, 1], [-.01, .01, 1]])
def test_rounding_rejects_unsupported_vectors(p):
    with pytest.raises(ValueError):
        matched.rounding_sensitivity(p, [1/3]*3)


def test_accounting_releases_only_known_completed_reservations():
    row = {"status": "valid", "reserve_usd": .15, "usage_cost_upper_estimate_usd": .02}
    assert matched.charge(row) == .02
    assert matched.charge({**row, "status": "transport_uncertain"}) == .15
    assert matched.charge({**row, "usage_cost_upper_estimate_usd": None}) == .15
    assert matched.charge({**row, "usage_cost_upper_estimate_usd": float('nan')}) == .15
    assert matched.charge({**row, "usage_cost_upper_estimate_usd": .20}) == .20


def test_incomplete_json_is_not_accepted_as_a_valid_response():
    response = {"model": matched.MODELS["openai"], "status": "incomplete", "output": []}
    with pytest.raises(ValueError, match="incomplete"):
        matched.parse_response("openai", response)


def test_freeze_excludes_answers_and_guards_network(tmp_path, monkeypatch):
    out = tmp_path / "matched"
    matched.prepare(out, matched.ROOT / "results/drag-development-v2")
    manifest = matched.verify(out)
    assert manifest["carry_in_usd"] == pytest.approx(.013161616)
    assert manifest["full_batch_reserved_upper_usd"] < 1
    plans = json.loads((out / "plans.json").read_text())
    assert len(plans) == 8
    for plan in plans:
        payload = json.dumps(plan["request"])
        assert plan["case_id"] not in payload
        for forbidden in ('\\"truth\\":', '\\"posterior\\":', '\\"episode\\":'):
            assert forbidden not in payload
    monkeypatch.setattr(matched, "load_key", lambda _: "test-only")
    monkeypatch.setattr(matched.urllib.request, "urlopen", lambda *a, **k: pytest.fail("network called"))
    (out / "pending.json").write_text("{}")
    with pytest.raises(SystemExit, match="Uncertain earlier"):
        matched.run(out, "openai", 4)
    (out / "pending.json").unlink()
    append(out / "api_ledger.jsonl", {"provider": "anthropic", "status": "transport_uncertain"})
    with pytest.raises(SystemExit, match="Uncertain earlier"):
        matched.run(out, "openai", 4)
    (out / "plans.json").write_text("[]")
    with pytest.raises(SystemExit, match="Frozen artifact changed"):
        matched.run(out, "openai", 4)
