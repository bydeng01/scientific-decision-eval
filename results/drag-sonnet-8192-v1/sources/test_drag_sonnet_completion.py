import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import drag_sonnet_completion as completion


def test_amendment_preserves_failure_changes_only_output_cap_and_bounds_spend(tmp_path, monkeypatch):
    source = completion.ROOT / "results/drag-matched-v1"
    out = tmp_path / "amendment"
    completion.prepare(out, source)
    manifest = completion.verify(out)
    assert manifest["carry_in_usd"] == pytest.approx(.377645116)
    assert manifest["full_batch_reserved_upper_usd"] < 1
    old = [p for p in json.loads((source / "plans.json").read_text()) if p["provider"] == "anthropic"]
    new = json.loads((out / "plans.json").read_text())
    assert len(new) == len(old) == 4
    for a,b in zip(old,new):
        expected = dict(a["request"], max_tokens=8192)
        assert b["request"] == expected
    carry = completion.read_lines(out / "carry_in.jsonl")
    failures = [r for r in carry if r["provider"] == "anthropic" and r["case_id"] == "dev-00-r1"]
    assert len(failures) == 1 and failures[0]["status"] == "invalid_response"
    monkeypatch.setattr(completion.urllib.request, "urlopen", lambda *a, **k: pytest.fail("network called"))
    (out / "pending.json").write_text("{}")
    with pytest.raises(SystemExit, match="no retry"):
        completion.run(out)
    (out / "pending.json").unlink()
    completion.append(out / "api_ledger.jsonl", {"status": "invalid_response"})
    with pytest.raises(SystemExit, match="no retry"):
        completion.run(out)
