"""Validate Choice definitions, review attribution, and saved references without modifying files."""

import argparse
import json
from pathlib import Path
import re


REVIEW = Path(__file__).resolve().parent
BASE = REVIEW.parent
ROOT = BASE.parent.parent


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f"Duplicate JSON key: {key}"
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)




def validate():
    inputs = read_json(REVIEW / "inputs.json")
    evaluation = read_json(REVIEW / "evaluation.json")
    checks = read_json(REVIEW / "checks.json")
    cases = {c["case_id"]: c for c in read_json(BASE / "inputs/cases.json")}
    evidence = {e["group_id"]: e for e in read_json(BASE / "inputs/evidence.json")}
    references = read_json(BASE / "evaluation/references.json")
    questions = {q["question_id"]: q for q in inputs["questions"]}
    document = (BASE / "CHOICES_REVIEW.md").read_text()
    log = (REVIEW / "REVIEW_LOG.md").read_text()

    assert len(cases) == 12 and len(evidence) == 6
    assert len({e["source_id"] for e in evidence.values()}) == 5
    assert len(questions) == len(inputs["questions"]) == 15
    assert sum(q["role"] == "engineering_simulation_only" for q in questions.values()) == 1
    assert set(questions) == set(evaluation["questions"])
    assert inputs["revision"] == evaluation["revision"] == checks["revision"]
    assert set(inputs["case_question_map"]) == set(cases) == set(evaluation["case_outcomes"])
    sections = dict(re.findall(r"^### ([^\n]+)\n(.*?)(?=^### |^## |\Z)", document, re.M | re.S))
    assert set(sections) == set(questions)

    for qid, question in questions.items():
        choice = question["question"]
        reference = evaluation["questions"][qid]
        section = sections[qid]
        assert question["review_status"] == "author_reviewed", qid
        assert reference["human_choice_review"] == "author_reviewed", qid
        assert reference["author_choice_review"] == "accepted_with_revisions", qid
        assert checks["per_question_human_choice_review"][qid] == reference["human_choice_review"]
        assert checks["per_question_author_choice_review"][qid] == reference["author_choice_review"]
        assert reference["expected_option"] in choice["criteria"], qid
        assert re.search(r"^\*\*Question:\*\* (.+)$", section, re.M)[1] == choice["instructions"], qid
        assert dict(re.findall(r"^\| `([^`]+)` \| (.+) \|$", section, re.M)) == choice["criteria"], qid
        assert "**Applies to:** " + ", ".join(question["case_ids"]) + "." in section, qid
        expected = "**Reference — evaluation only:** `" + reference["expected_option"] + "`. " + reference["rationale"]
        assert expected in section, qid
        assert "**Choice review:** Author reviewed; accepted with revisions." in section
        assert reference["review_note"] in log, qid
        assert f"| {qid} | Accepted with revisions | `{reference['expected_option']}` |" in log, qid
        conflict = "conflicting_assignment" if qid == "D03.specimen_assignment" else "conflicting"
        assert conflict in choice["criteria"] and f"Use {conflict} for unresolved contradictions" in choice["instructions"]
        for cid in question["case_ids"]:
            case = cases[cid]
            assert qid in inputs["case_question_map"][cid]
            assert question["state"]["scope"] == case["scope"]
            assert question["state"]["target_treatment"] == case["target_treatment"]
            assert question["state"]["evidence_text"] == evidence[case["group_id"]]["evidence_text"]
        change = checks["option_id_changes"][qid]
        assert change["removed"] == []

    for cid, ids in inputs["case_question_map"].items():
        assert len(ids) == len(set(ids)) and all(cid in questions[qid]["case_ids"] for qid in ids)
        assert cases[cid]["claim_text"] in document and cases[cid]["scope"]["text"] in document
        for field in ("count", "label", "action"):
            assert evaluation["case_outcomes"][cid][field] == references[cid][field]
        assert re.search(r"^\| \[" + re.escape(cid) + r"\]\(#[^)]*\) \| .* \| Author reviewed \|$", document, re.M)
    for item in evidence.values():
        assert "> " + item["evidence_text"].replace("\n", "\n> ") in document
    assert inputs["case_question_map"]["D03"] == ["D03.treatment_level", "D03.run_boundary", "D03.specimen_assignment"]
    assert "partial_identification" in questions["D03.run_boundary"]["question"]["criteria"]
    assert "partial_assignment" in questions["D03.specimen_assignment"]["question"]["criteria"]
    assert "mixing_batch" not in questions["D01-O.omitted_unit"]["question"]["criteria"]
    assert "scar_character" in questions["C02.identifier"]["question"]["criteria"]
    for cid in ("D01", "D01-S", "D01-O"):
        scope = cases[cid]["scope"]
        assert scope["same_mixing_operation"] and scope["same_curing_scheme"] and scope["age_days"] == 28
    for cid in ("C02", "C02-S"):
        scope = cases[cid]["scope"]
        assert scope["row_numbers"] == [1, 2, 3, 4, 5, 6]
        assert scope["part_ids"] == ["1A", "1B"] and scope["operators"] == ["O1", "O3"]

    # Whitelisted input structure keeps reference and review-rationale fields outside model inputs.
    assert set(inputs) == {"version", "revision", "status", "active_in_runner", "planned_model_calls", "case_question_map", "questions"}
    for question in questions.values():
        assert set(question) == {"question_id", "case_ids", "group_id", "review_status", "role", "state", "question"}
        assert set(question["state"]) == {"evidence_text", "target_treatment", "scope"}
        assert set(question["question"]) == {"type", "instructions", "criteria"}
        assert question["question"]["type"] == "choice"
    assert not re.search(r"[\u3400-\u9fff]", document + log + json.dumps(inputs, ensure_ascii=False) + json.dumps(evaluation, ensure_ascii=False))
    for href in re.findall(r"\]\(([^)]+)\)", document):
        if not href.startswith(("http://", "https://", "#")):
            assert (BASE / href.split("#")[0]).exists(), href

    assert evaluation["review"]["reviewer"] == "author"
    assert evaluation["review"]["reviewed_on"] == checks["review_attribution"]["reviewed_on"]
    assert checks["review_attribution"]["approval_scope"] == "prepared_review_as_a_whole"
    assert checks["review_attribution"]["human_confirmed_question_ids"] == []
    assert checks["review_attribution"]["author_reviewed_question_ids"] == list(questions)
    matrix = read_json(ROOT / "results/s2-nonbio-preflight-en-v1/call_matrix.json")
    assert matrix["status"] == "no_model_branch"
    assert all(row["base_calls"] == 0 and row["model"] is None and row["max_attempts_including_failures"] == 0 for row in matrix["rows"])
    assert inputs["active_in_runner"] is False and inputs["planned_model_calls"] == 0

    print("PASS: 15 questions; 12 items; document/JSON, review attribution and references verified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true", help=argparse.SUPPRESS)
    parser.parse_args()
    validate()
