"""Check the inactive Choice review artifacts without executing the task runner.

Run with --update-checks to record a successful validation and current hashes.
This checks file consistency and boundaries, not scientific correctness.
"""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo


REVIEW = Path(__file__).resolve().parent
BASE = REVIEW.parent
ROOT = BASE.parent.parent
SNAPSHOT = REVIEW / "history/initial-drafts"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f"Duplicate JSON key: {key}"
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(update_checks=False, check_history=True):
    inputs = read_json(REVIEW / "inputs.json")
    evaluation = read_json(REVIEW / "evaluation.json")
    checks = read_json(REVIEW / "checks.json")
    initial_inputs = read_json(SNAPSHOT / "inputs.json") if check_history else None
    initial_evaluation = read_json(SNAPSHOT / "evaluation.json") if check_history else None
    cases = {c["case_id"]: c for c in read_json(BASE / "inputs/cases.json")}
    evidence = {e["group_id"]: e for e in read_json(BASE / "inputs/evidence.json")}
    references = read_json(BASE / "evaluation/references.json")
    questions = {q["question_id"]: q for q in inputs["questions"]}
    initial_questions = {q["question_id"]: q for q in initial_inputs["questions"]} if check_history else None
    document = (BASE / "CHOICES_REVIEW.md").read_text()
    log = (REVIEW / "REVIEW_LOG.md").read_text()

    assert len(cases) == 12 and len(evidence) == 6
    assert len({e["source_id"] for e in evidence.values()}) == 5
    assert len(questions) == len(inputs["questions"]) == 15
    assert sum(q["role"] == "engineering_simulation_only" for q in questions.values()) == 1
    assert set(questions) == set(evaluation["questions"])
    if check_history:
        assert set(questions) == set(initial_questions)
    assert inputs["revision"] == evaluation["revision"] == checks["revision"]
    if check_history:
        assert inputs["case_question_map"] == initial_inputs["case_question_map"]
    assert set(inputs["case_question_map"]) == set(cases) == set(evaluation["case_outcomes"])
    sections = dict(re.findall(r"^### ([^\n]+)\n(.*?)(?=^### |^## |\Z)", document, re.M | re.S))
    assert set(sections) == set(questions)

    for qid, question in questions.items():
        choice = question["question"]
        reference = evaluation["questions"][qid]
        section = sections[qid]
        if check_history:
            assert question["state"] == initial_questions[qid]["state"], qid
        if check_history:
            assert question["case_ids"] == initial_questions[qid]["case_ids"], qid
        assert question["review_status"] == "user_approved", qid
        assert reference["human_choice_review"] == "user_approved", qid
        assert reference["user_choice_review"] == "accepted_with_revisions", qid
        assert checks["per_question_human_choice_review"][qid] == reference["human_choice_review"]
        assert checks["per_question_user_choice_review"][qid] == reference["user_choice_review"]
        if check_history:
            assert reference["expected_option"] == initial_evaluation["questions"][qid]["expected_option"]
        assert reference["expected_option"] in choice["criteria"], qid
        if check_history:
            assert set(initial_questions[qid]["question"]["criteria"]) <= set(choice["criteria"]), qid
        assert re.search(r"^\*\*Question:\*\* (.+)$", section, re.M)[1] == choice["instructions"], qid
        assert dict(re.findall(r"^\| `([^`]+)` \| (.+) \|$", section, re.M)) == choice["criteria"], qid
        assert "**Applies to:** " + ", ".join(question["case_ids"]) + "." in section, qid
        expected = "**Reference — evaluation only:** `" + reference["expected_option"] + "`. " + reference["rationale"]
        assert expected in section, qid
        assert "**Choice review:** User approved; accepted with revisions." in section
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
        if check_history:
            assert change["added"] == [k for k in choice["criteria"] if k not in initial_questions[qid]["question"]["criteria"]]

    for cid, ids in inputs["case_question_map"].items():
        assert len(ids) == len(set(ids)) and all(cid in questions[qid]["case_ids"] for qid in ids)
        assert cases[cid]["claim_text"] in document and cases[cid]["scope"]["text"] in document
        for field in ("count", "label", "action"):
            assert evaluation["case_outcomes"][cid][field] == references[cid][field]
        assert re.search(r"^\| \[" + re.escape(cid) + r"\]\(#[^)]*\) \| .* \| User approved \|$", document, re.M)
    if check_history:
        assert evaluation["case_outcomes"] == initial_evaluation["case_outcomes"]
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

    if check_history:
        for name, entry in read_json(SNAPSHOT / "manifest.json")["files"].items():
            assert sha256(SNAPSHOT / name) == entry["sha256"], name
        original_checks = read_json(SNAPSHOT / "checks.json")
        assert checks["protected_sha256_unchanged"] == original_checks["protected_sha256_unchanged"]
        for relative, digest in checks["protected_sha256_unchanged"].items():
            assert sha256(ROOT / relative) == digest, relative
        # Only the Choice navigation paragraph changed in the inherited source-review document.
        current_source_review = (BASE / "ALL_CASES_REVIEW.md").read_text()
        initial_source_review = (SNAPSHOT / "ALL_CASES_REVIEW.md").read_text()
        assert current_source_review.split("## 1. Sources and case groups")[1] == initial_source_review.split("## 1. Sources and case groups")[1]
    assert evaluation["review"]["reviewer"] == "user"
    assert evaluation["review"]["user_approved_on"] == checks["review_session"]["user_approved_on"]
    assert checks["review_session"]["approval_scope"] == "prepared_review_as_a_whole"
    assert checks["review_session"]["human_confirmed_question_ids"] == []
    assert checks["review_session"]["user_approved_question_ids"] == list(questions)
    matrix = read_json(ROOT / "results/s2-nonbio-preflight-en-v1/call_matrix.json")
    assert matrix["status"] == "no_model_branch"
    assert all(row["base_calls"] == 0 and row["model"] is None and row["max_attempts_including_failures"] == 0 for row in matrix["rows"])
    assert inputs["active_in_runner"] is False and inputs["planned_model_calls"] == 0

    if update_checks:
        checks["artifact_sha256"]["choice-review-v1/verify_review.py"] = sha256(Path(__file__))
        checks["artifact_sha256"] = {relative: sha256(BASE / relative) for relative in checks["artifact_sha256"]}
        checks["latest_validation"] = {
            "status": "passed",
            "performed_at": datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds"),
            "command": "python3 development/s2-nonbio-v1/choice-review-v1/verify_review.py --update-checks",
            "method": "Offline static artifact checks; no runner execution, source download, or model API call.",
            "passed_checks": [
                "JSON parsing rejects duplicate keys; 15 unique definitions cover 12 items, 6 groups and 5 sources",
                "Exact document/JSON instructions, option IDs and descriptions, applicability, references and rationales",
                "Bidirectional case/question links; unchanged supplied evidence, targets and scopes",
                "All 15 per-question delegated-review decisions match the log; no human confirmation inferred",
                "All reference option IDs and case outcomes unchanged; added option IDs accounted for",
                "D01 scope, three D03 questions, omission fixture and corrected C02 six-row scope retained",
                "Input fields exclude answer-key annotations; reviewed artifact text is English",
                "Local review-document links exist; snapshot file hashes match the original manifest",
                "Protected active inputs, references, code, budget, call matrix and frozen contribution hashes unchanged",
                "Inherited source-review content unchanged beyond its Choice navigation paragraph",
                "Existing call matrix records zero calls and draft flags remain inactive",
                "Artifact SHA-256 hashes updated and verified"
            ],
            "not_performed": ["Independent human annotation", "New source audit", "Active runner execution", "Model API calls or training"]
        }
        (REVIEW / "checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n")
    if check_history:
        for relative, digest in checks["artifact_sha256"].items():
            assert sha256(BASE / relative) == digest, relative
    print("PASS: 15 questions; 12 items; document/JSON, review attribution and references verified. Historical hashes checked:", check_history)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update-checks", action="store_true")
    parser.add_argument("--release", action="store_true", help="Validate published content without private historical files")
    args = parser.parse_args()
    if args.release and args.update_checks:
        parser.error("--release is read-only")
    validate(args.update_checks, check_history=not args.release)
