"""Validate the biological cases, reference answers, source assets, and derived outputs without modifying files."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

from derive import derive
from render_review import documents

B = Path(__file__).resolve().parent
ROOT = B.parents[2]


def read(name):
    return json.loads((B / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def reviewed_input_sha(problem, revisions, decision_id):
    """Check the exact source edits while retaining the original review hash."""
    matches = [r for r in revisions if r["problem_id"] == problem["problem_id"]]
    assert len(matches) <= 1
    restored = copy.deepcopy(problem)
    for revision in matches:
        assert revision["prior_decision_id"] == decision_id
        assert canonical_sha(restored) == revision["after_problem_input_sha256"]
        assert revision["edits"]
        for edit in revision["edits"]:
            path = edit["path"]
            assert path in [["evidence", 0, "text"], ["records", "record_origin"]]
            parent = restored
            for key in path[:-1]:
                parent = parent[key]
            assert parent[path[-1]] == edit["after"]
            parent[path[-1]] = edit["before"]
        assert canonical_sha(restored) == revision["before_problem_input_sha256"]
    return canonical_sha(restored)


def reference_content(evaluation):
    return {"questions": [{k: q[k] for k in ("question_id", "reference_option", "rationale", "downstream_role")}
                          for q in evaluation["questions"]],
            **{k: evaluation[k] for k in ("deterministic_work", "inference_boundary", "expected_code_output")}}




def validate():
    inputs, evaluation = read("inputs.json"), read("evaluation.json")
    inventory, statuses = read("collection_inventory.json"), read("review_status.json")
    sources = read("sources.json")["source_records"]
    ps, es = inputs["problems"], evaluation["problems"]
    pids = [p["problem_id"] for p in ps]
    qids = [q["question_id"] for p in ps for q in p["questions"]]
    assert pids == ["B001", "B002", "B003", "B004"]
    assert len(qids) == len(set(qids)) == 8
    assert evaluation["evaluation_only"] is True
    assert pids == [e["problem_id"] for e in es]
    sids = [s["source_id"] for s in sources]
    assert len(sids) == len(set(sids)) == 4

    old = json.loads((ROOT / "development/s2-nonbio-v1/inputs/evidence.json").read_text())
    expansion = json.loads((ROOT / "development/s2-nonbio-expansion/batch-001/inputs.json").read_text())
    expansion_refs = json.loads((ROOT / "development/s2-nonbio-expansion/batch-001/evaluation.json").read_text())
    old_choices = json.loads((ROOT / "development/s2-nonbio-v1/choice-review-v1/inputs.json").read_text())
    old_ids = [p["group_id"] for p in old]
    exp_ids = [p["problem_id"] for p in expansion["problems"]]
    old_qids = {q["question_id"] for q in old_choices["questions"]}
    old_qids |= {q["question_id"] for p in expansion["problems"] for q in p["questions"]}
    assert not set(qids) & old_qids
    assert len(set(old_ids + exp_ids + pids)) == 20
    assert inventory["original_groups"] == old_ids and len(old_ids) == 6
    assert inventory["completed_expansion_batches"][0]["groups"] == exp_ids and len(exp_ids) == 10
    assert inventory["completed_expansion_batches"][0]["review_summary"] == expansion_refs["review_summary"]
    assert expansion_refs["review_summary"]["pending_problems"] == 0
    assert expansion_refs["review_summary"]["pending_questions"] == 0
    assert inventory["existing_group_count"] == 16
    assert inventory["collection_total_after_addition"] == 20
    assert inventory["new_group_ids"] == pids and inventory["new_question_count"] == 8
    assert not inventory["in_progress_expansion_batches_before_this_addition"]
    assert set(statuses["groups"]) == set(pids)
    decisions = read("review_decisions.json")["decisions"]
    source_revision = read("source_revisions.json")
    assert source_revision["authorized_by"] == "author" and source_revision["summary"]
    assert source_revision["references_changed"] is False
    revisions = source_revision["input_revisions"]
    assert [r["problem_id"] for r in revisions] == ["B004"]
    assert len({d["decision_id"] for d in decisions}) == len(decisions)
    accepted_groups, accepted_questions = {}, {}
    for decision in decisions:
        assert decision["reviewer"] == "author" and decision["decision"] == "accepted_as_proposed"
        assert decision["author_review_summary_english"] and decision["decision_id"] and decision["approved_questions"]
        for pid in decision["approved_problem_ids"]:
            assert pid in pids and pid not in accepted_groups
            p = next(p for p in ps if p["problem_id"] == pid)
            e = next(e for e in es if e["problem_id"] == pid)
            assert reviewed_input_sha(p, revisions, decision["decision_id"]) == decision["approved_problem_input_sha256"][pid]
            assert canonical_sha(reference_content(e)) == decision["approved_reference_content_sha256"][pid]
            assert all(q["question_id"] in decision["approved_questions"] for q in p["questions"])
            accepted_groups[pid] = decision["decision_id"]
        for qid, record in decision["approved_questions"].items():
            assert qid in qids and qid not in accepted_questions
            q = next(q for p in ps for q in p["questions"] if q["question_id"] == qid)
            assert canonical_sha(q) == record["question_input_sha256"]
            accepted_questions[qid] = (decision["decision_id"], record["reference_option"])
    assert statuses["case_content_approved_by_author"] == (len(accepted_groups) == len(ps))
    assert inventory["accepted_new_groups"] == len(accepted_groups)
    assert inventory["pending_new_groups"] == len(ps) - len(accepted_groups)

    forbidden = {"reference_option", "rationale", "expected_code_output", "review_status", "reviewed_by", "approved_by_author", "final_label"}
    def clean_inputs(item):
        if isinstance(item, dict):
            assert not set(item) & forbidden
            for v in item.values():
                clean_inputs(v)
        elif isinstance(item, list):
            for v in item:
                clean_inputs(v)
    clean_inputs(inputs)

    fallback_checks = 0
    for p, e in zip(ps, es):
        pid = p["problem_id"]
        assert re.fullmatch(r"B\d{3}", pid)
        assert len(p["questions"]) == 2
        assert set(p["source_ids"]) <= set(sids)
        assert {x["source_id"] for x in p["evidence"]} == set(p["source_ids"])
        assert all(x["location"] and x["text"] for x in p["evidence"])
        assert p["claim_origin"] == "benchmark_constructed_not_a_source_author_claim"
        assert [q["question_id"] for q in p["questions"]] == [q["question_id"] for q in e["questions"]]
        expected_group_status = "author_reviewed" if pid in accepted_groups else "pending_author_review"
        assert e["review_status"] == statuses["groups"][pid]["status"] == expected_group_status
        assert set(statuses["groups"][pid]["questions"]) == {q["question_id"] for q in p["questions"]}
        answers = {q["question_id"]: q["reference_option"] for q in e["questions"]}
        for i, (q, ref) in enumerate(zip(p["questions"], e["questions"]), 1):
            qid = q["question_id"]
            assert qid == f"{pid}-Q{i:02d}"
            assert {"other", "not_stated", "conflicting"} <= set(q["options"])
            assert all(isinstance(x, str) and x.strip() for x in q["options"].values())
            for fragment in ["Select exactly one", "missing, partial, or ambiguous", "conflicting before", "Do not count"]:
                assert fragment in q["instruction"]
            assert ref["reference_option"] in q["options"] and ref["rationale"] and ref["downstream_role"]
            accepted = qid in accepted_questions
            expected_status = "author_reviewed" if accepted else "pending_author_review"
            decision_id = accepted_questions[qid][0] if accepted else None
            assert ref["review_status"] == expected_status and ref["approved_by_author"] is accepted
            assert statuses["groups"][pid]["questions"][qid] == {
                "status": expected_status, "approved_by_author": accepted, "decision": decision_id}
            if accepted:
                assert ref["reference_option"] == accepted_questions[qid][1]
                assert ref["approval_decision_id"] == decision_id
                assert ref["reviewed_by"] == "author"
            for choice, output in [("other", "candidate_completion_required"),
                                   ("not_stated", "insufficient_evidence"),
                                   ("conflicting", "evidence_conflict")]:
                candidate = dict(answers, **{qid: choice})
                result = derive(p, candidate)
                assert result == {"status": output, "counts": None, "clauses": None, "final_label": None}
                fallback_checks += 1
        assert derive(p, answers) == e["expected_code_output"]
        try:
            derive(p, {})
        except ValueError:
            pass
        else:
            raise AssertionError("Missing answer was silently treated as source evidence")
        mixed = {p["questions"][0]["question_id"]: "not_stated", p["questions"][1]["question_id"]: "conflicting"}
        assert derive(p, mixed)["status"] == "evidence_conflict"

    # Selected-arm scope and donor identity matter independently of row count.
    pooling = copy.deepcopy(ps[2])
    answers = {q["question_id"]: q["reference_option"] for q in es[2]["questions"]}
    pooling["records"]["pools"] = [p for p in pooling["records"]["pools"] if p["pool_size"] == 8]
    assert derive(pooling, answers) == es[2]["expected_code_output"]
    for pool in pooling["records"]["pools"]:
        if pool["pool_id"].endswith("2"):
            pool["contributors"] = ["new_" + c for c in pool["contributors"]]
    result = derive(pooling, answers)
    assert result["counts"]["distinct_contributors"] == 32
    assert result["clauses"]["distinct_mice"] == "consistent"
    assert result["counts"]["separately_observed_contributor_profiles"] == 0
    assert es[3]["expected_code_output"]["counts"]["validated_new_germline_lines"] is None
    assert es[0]["expected_code_output"]["counts"]["distinct_F0_ancestors"] is None
    assert es[1]["expected_code_output"]["counts"]["exact_mutation_origins"] is None

    for name, expected in documents().items():
        assert (B / name).read_text() == expected, f"Markdown/JSON mismatch: {name}"
    omitted = set()
    manifest = json.loads((ROOT / 'release-sha256.json').read_text())
    prefix = B.relative_to(ROOT).as_posix() + '/'
    omitted = {p[len(prefix):] for p in manifest.get('omitted_source_assets', []) if p.startswith(prefix)}
    assert all(not (B / p).exists() for p in omitted), 'Omitted source asset was restored'
    assert omitted <= {p for s in sources for p in s['local_files']}
    asset_count = 0
    for source in sources:
        assert source["verified_locations"] and source["limitations"]
        for path, digest in source["local_files"].items():
            if path in omitted:
                continue
            assert sha(B / path) == digest, f"Source asset changed: {path}"
            asset_count += 1
    retained = {path for s in sources for path in s["local_files"]}
    for d in read("download_log.json"):
        if d["retained_asset"]:
            assert d["file"] in retained and "error" not in d
            if "sha256" in d and d["file"] not in omitted:
                assert sha(B / d["file"]) == d["sha256"]
    file_revisions = source_revision["preexisting_file_revisions"]
    appendices = source_revision["preserved_review_appendices"]
    review_path = "development/s2-nonbio-expansion/batch-001/review_decisions.json"
    assert set(appendices) == {review_path}
    appendix = appendices[review_path]
    review_text = (ROOT / review_path).read_text()
    review_data = json.loads(review_text)
    assert list(review_data) == ["batch_id", "decisions", "follow_up_reviews"]
    assert [r["follow_up_id"] for r in review_data["follow_up_reviews"]] == appendix["follow_up_ids"] == ["UR005-F01"]
    assert all(r["reviewer"] == "author" for r in review_data["follow_up_reviews"])
    allowed = {"development/s2-nonbio-expansion/batch-001/" + name for name in
               ["inputs.json", "sources.json", "BATCH_REVIEW.md", "REVIEW_LOG.md",
                "verify_batch.py", "checks.json", "checks.sha256"]}
    assert set(file_revisions) <= allowed & set(inventory["preexisting_file_sha256"])
    return {"existing_groups": 16, "new_groups": 4, "collection_total": 20,
            "new_questions": 8, "accepted_groups": len(accepted_groups),
            "accepted_questions": len(accepted_questions),
            "pending_groups": 4 - len(accepted_groups), "pending_questions": 8 - len(accepted_questions),
            "reference_output_checks": 4, "fallback_answer_checks": fallback_checks,
            "source_assets_verified": asset_count,
            "source_assets_omitted": sorted(omitted),
            "preexisting_files_with_authorized_revisions": len(file_revisions),
            "preexisting_files_with_preserved_review_appendices": len(appendices),
            "authorized_source_qualifications": len(revisions),
            "checks": ["Unique IDs and exact reference coverage", "Markdown matches JSON",
                       "Author decisions match accepted content hashes and review states", "Source asset hashes",
                       "Known source records and deterministic outputs agree",
                       "Pool scope filtering and donor deduplication",
                       "Unknown ancestry, mutation origins, and germline counts remain null",
                       "Fallback precedence and missing-answer rejection",
                       "Exact source revisions checked"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true", help=argparse.SUPPRESS)
    parser.parse_args()
    print(json.dumps({"status": "passed", "scope": "published_content", **validate()}, indent=2))


if __name__ == "__main__":
    main()
