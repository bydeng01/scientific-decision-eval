from pathlib import Path
import sys
import json

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from document_pilot import cases, gold, MODELS, request_payload, reserve_cost, validate_response


def test_case_balance_and_gold_invariance_to_distractors():
    data = cases()
    assert len(data) == 32
    for family in {c["family"] for c in data}:
        group = [c for c in data if c["family"] == family]
        assert sum(c["eligible"] for c in group) == 4
        assert len({tuple(c["labels"].values()) for c in group}) == 8
    # These documents have 23 completed credits plus planned/transfer/duplicate rows.
    for case in data:
        labels, action = gold(case["record"])
        assert labels == case["labels"] and action == case["eligible"]


def test_policy_expected_actions_from_named_predicates():
    for case in cases():
        b = case["labels"]
        assert case["eligible"] == (b["renewal_ok"] if b["is_renewal"] else b["new_ok"])


def test_only_document_not_gold_goes_to_api_and_budget_is_bounded():
    total = 0
    for case in cases():
        for model in MODELS:
            for mode in ("nodes", "direct"):
                payload = request_payload(model, mode, case["document"])
                assert payload["messages"][-1]["content"].endswith(case["document"])
                assert "labels" not in payload and "eligible" not in payload
                assert payload["provider"]["require_parameters"]
                total += reserve_cost(payload)
    assert total < 1.0


@pytest.mark.parametrize("content", ['{"eligible":1.1}', '{"eligible":true}', '{"eligible":NaN}', '{"eligible":0.8,"extra":1}', 'not json'])
def test_invalid_outputs_are_rejected_without_repairs(content):
    response = {"choices":[{"finish_reason":"stop","message":{"content":content}}]}
    with pytest.raises((ValueError, TypeError)):
        validate_response(response,"direct")


def test_valid_score_kept_exactly():
    response = {"choices":[{"finish_reason":"stop","message":{"content":json.dumps({"eligible":.8123})}}]}
    assert validate_response(response,"direct") == {"eligible":.8123}
