"""Offline second audit: raw-answer recount and scoring sensitivity probes."""
import copy
from collections import Counter
import hashlib
import json
from pathlib import Path
import socket
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True


def blocked(*args, **kwargs):
    raise RuntimeError("This audit cannot access networks or credentials")


socket.socket = socket.create_connection = blocked


def audit(event, args):
    if event.startswith("socket."):
        blocked()
    if event == "open" and isinstance(args[0], (str, bytes)):
        name = Path(args[0].decode() if isinstance(args[0], bytes) else args[0]).name
        if name.startswith(".env"):
            blocked()


sys.addaudithook(audit)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


previous = ROOT / "results/s2-thirteen-model-analysis-v1"
protected = read(previous / "protected-sha256.json")
protected.update({str(p.relative_to(ROOT)): sha(p) for p in previous.iterdir() if p.is_file()})
assert all(sha(ROOT / p) == h for p, h in protected.items())
summary = read(previous / "summary.json")
model_recount = {}
http = Counter()
errors = []
raw_responses = []
groups = None
refs = None
for directory in ("s2-execution-live-v1", "s2-execution-extension-live-v1",
                  "s2-execution-glm-kimi-live-v1"):
    base = ROOT / "results" / directory
    config = read(base / "config.json")
    models = {m["id"]: m for m in config["models"]}
    groups = read(base / "inputs.json")
    refs = read(base / "evaluation_only/references.json")
    for job in read(base / "plan.json")["jobs"]:
        mid = job["model_id"]
        model = models[mid]
        d = base / "attempts" / job["job_id"]
        intent, receipt, saved = (read(d / (n + ".json")) for n in ("intent", "receipt", "prediction"))
        assert intent["request"] == job["request"] and intent["attempt"] == 1
        http[str(receipt["http_status"])] += 1
        row = model_recount.setdefault(mid, Counter())
        row["requests"] += 1
        row["planned_answers"] += len(job["question_map"])
        answers = {}
        if receipt["http_status"] == 200:
            raw = json.loads(receipt["raw_body"])
            raw_responses.append((model["provider"], raw["id"]))
            assert raw["model"] in model["accepted_response_models"]
            if model["provider"] == "openrouter":
                assert raw["provider"] == "TypeSafe"
                payload = {k: v["choice"] for k, v in raw["answers"].items()}
                for k, v in raw["answers"].items():
                    assert set(v["probabilities"]) == set(job["packet"]["questions"][k]["criteria"])
                    assert v["probabilities"][v["choice"]] == max(v["probabilities"].values())
            elif model["provider"] == "openrouter_chat":
                assert raw["provider"] in model["accepted_response_providers"]
                assert len(raw["choices"]) == 1 and raw["choices"][0]["finish_reason"] == "stop"
                payload = json.loads(raw["choices"][0]["message"]["content"])
            elif model["provider"] == "openai":
                assert raw["status"] == "completed"
                texts = [c["text"] for item in raw["output"] if item["type"] == "message"
                         for c in item["content"] if c["type"] == "output_text"]
                assert len(texts) == 1
                payload = json.loads(texts[0])
            else:
                assert raw["stop_reason"] == "end_turn"
                texts = [c["text"] for c in raw["content"] if c["type"] == "text"]
                assert len(texts) == 1
                payload = json.loads(texts[0])
            assert set(payload) == set(job["question_map"])
            for k, v in payload.items():
                assert v in job["packet"]["questions"][k]["criteria"]
                answers[job["question_map"][k]] = v
            row["successful_requests"] += 1
        assert answers == saved["answers"]
        for qid in job["question_map"].values():
            if qid not in answers:
                row["absent"] += 1
            elif answers[qid] == refs["answers"][qid]:
                row["correct"] += 1
            else:
                row["semantic_errors"] += 1
                errors.append({"job_id": job["job_id"], "question_id": qid,
                               "prediction": answers[qid], "reference": refs["answers"][qid]})
        if saved["derived"] is not None:
            row["canonical_inconsistent_labels"] += saved["derived"]["final_label"] == "inconsistent"
        if job["group_id"] == "B002" and answers:
            # Independent arithmetic/membership check for the sole observed error case.
            problem = next(g["problem"] for g in groups if g["group_id"] == "B002")
            records = {r["experiment"]: r["resistant_colonies"] for r in problem["records"]["series"]}
            mapping = {"shared_then_separate": (1, 10), "separate_then_shared": (10, 1),
                       "both_shared": (1, 1), "both_separate": (10, 10)}
            history = dict(zip(("11a", "11"), mapping[answers["B002-Q01"]]))
            assert saved["derived"]["counts"]["growth_histories"] == history
            assert saved["derived"]["counts"]["colony_totals"] == {k: sum(v) for k, v in records.items()}
            assert saved["derived"]["counts"]["exact_mutation_origins"] is None
assert len(raw_responses) == len(set(raw_responses)) == 597
for mid, r in model_recount.items():
    old = summary["models"][mid]
    assert r["correct"] == old["semantic_fixed"]["correct"]
    assert r["planned_answers"] == old["semantic_fixed"]["denominator"]
    assert r["successful_requests"] == old["successful_requests"]
    assert r["semantic_errors"] == old["choice_categories"].get("semantic_error", 0)

# Reuse the actual scorer only for adversarial probes, after independent recounting.
sys.path.insert(0, str(ROOT / "development/s2-execution-v3"))
from derive import derive
from scoring import projection, score_lane

masked = []
probes = 0
ignored = []
labels = []
for g in groups:
    if g["route"] != "model":
        continue
    gid = g["group_id"]
    answers = {q["question_id"]: refs["answers"][q["question_id"]] for q in g["questions"]}
    reference = derive(g, answers)
    labels.append({"group_id": gid, "canonical_final_label": reference["final_label"],
                   "reported_label": reference["output"]["claim_assessment"]
                   if g["package"] == "nonbio" else reference["final_label"]})
    for q in g["questions"]:
        for option in q["question"]["criteria"]:
            qid = q["question_id"]
            if option == answers[qid]:
                continue
            probes += 1
            changed = answers | {qid: option}
            result = derive(g, changed)
            lane = {(0, gid): {"answers": changed, "derived": result}}
            scored = score_lane([g], refs, lane, 1)
            assert scored["model_routed_semantic_choices"]["correct"] == 1
            assert scored["group_semantic_and_outcome_exact"]["correct"] == 0
            if scored["scientific_claims"]["exact"]["correct"]:
                masked.append({"question_id": qid, "wrong_option": option,
                               "entire_derived_object_unchanged": result == reference})
    if g["package"] == "nonbio":
        for field, value in (("status", "invalid"), ("clauses", {"injected": "invalid"}),
                             ("final_label", "consistent")):
            changed = copy.deepcopy(reference)
            changed[field] = value
            scored = score_lane([g], refs, {(0, gid): {"answers": answers, "derived": changed}}, 1)
            assert scored["scientific_claims"]["exact"]["correct"] == 1
            assert scored["group_semantic_and_outcome_exact"]["correct"] == 1
            ignored.append({"group_id": gid, "field": field,
                            "full_projection_exact": True, "joint_metric_exact": True})

assert probes == 109 and len(masked) == 17 and len(ignored) == 18
assert sum(x["entire_derived_object_unchanged"] for x in masked) == 10
assert all(r["canonical_final_label"] == "inconsistent" for r in labels)
assert all(sha(ROOT / p) == h for p, h in protected.items())
result = {"raw_recount": model_recount, "http_status_counts": http,
          "semantic_errors": errors, "unique_success_response_ids": len(raw_responses),
          "single_wrong_option_probes": probes, "masked_by_outcome_projection": masked,
          "unscored_nonbio_field_corruptions": ignored, "label_granularity": labels,
          "unchanged_existing_files": len(protected),
          "new_model_calls": 0, "credential_files_read": 0,
          "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in
                            [ROOT / "development/s2-execution-v3/derive.py",
                             ROOT / "development/s2-execution-v3/scoring.py", HERE / "check.py"]}}
payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
output = HERE / "checks.json"
if output.exists():
    assert output.read_text() == payload, "Use a new audit directory when inputs change"
else:
    output.write_text(payload)
print(json.dumps({"requests": sum(r["requests"] for r in model_recount.values()),
                  "correct": sum(r["correct"] for r in model_recount.values()),
                  "semantic_errors": len(errors), "masked_probes": len(masked),
                  "ignored_field_corruptions": len(ignored),
                  "unchanged_existing_files": len(protected)}))
