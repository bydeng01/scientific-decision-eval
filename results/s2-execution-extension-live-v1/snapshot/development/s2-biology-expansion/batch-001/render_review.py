"""Render review documents from the separate input, reference, and review records."""
import json
import os
from pathlib import Path

B = Path(__file__).resolve().parent


def read(name):
    return json.loads((B / name).read_text())


def block(value):
    return "```json\n" + json.dumps(value, indent=2) + "\n```"


def evidence_link(path):
    if (B / path).is_file():
        return path
    root = next(parent for parent in B.parents if (parent / "release-sha256.json").is_file())
    return Path(os.path.relpath(root / "development/s2-biology-expansion/batch-001" / path, B)).as_posix()


def documents():
    ps = read("inputs.json")["problems"]
    es = {e["problem_id"]: e for e in read("evaluation.json")["problems"]}
    ss = {s["source_id"]: s for s in read("sources.json")["source_records"]}
    status = read("review_status.json")
    decisions = read("review_decisions.json")["decisions"]
    source_revision = read("source_revisions.json")
    revised_groups = {r["problem_id"] for r in source_revision["input_revisions"]}
    inventory = read("collection_inventory.json")
    approved_groups = sum(g["status"] == "author_reviewed" for g in status["groups"].values())
    approved_questions = sum(q["approved_by_author"] for g in status["groups"].values() for q in g["questions"].values())
    index = ["| Group | Scientific distinction | Questions | Status |",
             "| --- | --- | --- | --- |"]
    short = ["Developmental exposure of future-generation germ cells",
             "Clonal amplification separates mutation origins from colony counts",
             "Pre-assay pooling merges outcomes and reuses the same contributors",
             "Somatic mosaicism and a non-specific germline phenotype marker"]
    for p, distinction in zip(ps, short):
        pid = p["problem_id"]
        index.append(f"| [{pid}](BATCH_REVIEW.md#{pid.lower()}) | {distinction} | {len(p['questions'])} | {status['groups'][pid]['status']} |")
    index = "\n".join(index)
    counts = (f"The collection contains {inventory['existing_group_count']} non-biological groups "
              f"and {len(ps)} biological groups: **{inventory['collection_total_after_addition']} total**. "
              f"Author-reviewed biological references cover {approved_groups} groups and {approved_questions} Choices. "
              "Review attribution for the original and non-biological expansion groups is recorded in their case packages.")
    docs = {}
    docs["README.md"] = ("# Biological S2 expansion, batch 001\n\n" + counts + "\n\n" + index +
        "\n\n[BATCH_REVIEW.md](BATCH_REVIEW.md) contains all four groups and their reference answers.\n\n"
        "`inputs.json` contains evidence, structured records, claims, and Choices. `evaluation.json` contains reference answers, rationales, inference boundaries, and expected code outputs. "
        "`derive.py` performs offline bookkeeping from supplied semantic answers; its outputs are conditional on those answers. "
        "[SOURCE_REVIEW.md](SOURCE_REVIEW.md) records source locations and inspection limits. "
        "[REVIEW_LOG.md](REVIEW_LOG.md) records each question's status. `collection_inventory.json` preserves the prior inventory and file hashes.\n\n"
        "Run from the repository root:\n\n```sh\npython3 -B development/s2-biology-expansion/batch-001/verify_batch.py --release\n```\n\n"
        "After editing case documentation, regenerate Markdown with `render_review.py` and check it with `verify_batch.py --release`. "
        "For published-file checksums and saved model scores, run `python3 -B scripts/verify_release.py` from the repository root. "
        "Historical `--write-checks` requires the original private archive. These checks establish artifact consistency, not scientific correctness.\n")
    groups = []
    for p in ps:
        pid = p["problem_id"]
        e = es[pid]
        approved = status["groups"][pid]["status"] == "author_reviewed"
        review_note = ("Status: **author_reviewed**. Author review covers both Choices, reference answers, evidence scope, and inference boundary."
                       if approved else "Status: **pending_author_review**. Proposed references await author review.")
        if pid in revised_groups:
            review_note += (" Source wording was qualified on 2026-09-21; "
                            "Choices and reference answers retain their original review attribution. "
                            "See [source_revisions.json](source_revisions.json).")
        lines = [f'<a id="{pid.lower()}"></a>', f"## {pid}: {p['title']}",
                 review_note,
                 f"**Target treatment:** {p['target_treatment']}", f"**Scope:** {p['scope']}",
                 "### Source evidence"]
        for sid in p["source_ids"]:
            s = ss[sid]
            lines.append(f"[{sid}]({s['url']}): {s['citation']} DOI: {s['doi']}. {s['version']}")
        for i, ev in enumerate(p["evidence"], 1):
            lines += [f"**Evidence {i} — {ev['location']}**", ev["text"]]
        lines += ["These passages are source-faithful adaptations, not verbatim quotations.",
                  "### Claim to assess", p["scientific_claim"],
                  "This claim was constructed for the case; it is not attributed to the source authors.",
                  "### Structured source records", block(p["records"]),
                  "### Atomic Choices"]
        for q in p["questions"]:
            lines += [f"#### {q['question_id']}", q["instruction"],
                      "\n".join(f"- **`{key}`**: {description}" for key, description in q["options"].items())]
        lines += ["### " + ("Accepted" if approved else "Proposed") + " reference answers — evaluation only"]
        for r in e["questions"]:
            lines += [f"**{r['question_id']}: `{r['reference_option']}`** — {r['review_status']}",
                      r["rationale"], "Downstream role: " + r["downstream_role"]]
        lines += ["### Deterministic derivation", e["deterministic_work"],
                  "Expected output with the " + ("accepted" if approved else "proposed") + " references:", block(e["expected_code_output"]),
                  "A missing or illegal answer is an input error. `conflicting`, `other`, and `not_stated` stop group-level composition, in that precedence order. "
                  "Unknown scientific quantities remain null. With substantive answers, an inconsistent clause makes the conjunction inconsistent; an unknown clause remains separately visible.",
                  "### Inference boundary", e["inference_boundary"]]
        groups.append("\n\n".join(lines))
    docs["BATCH_REVIEW.md"] = "# Biological S2 case review\n\n" + counts + "\n\n" + index + "\n\n" + "\n\n---\n\n".join(groups) + "\n"
    log = ["# Biological S2 review log", status["review_rule"],
           f"The author accepted {approved_groups} biological groups and {approved_questions} Choices. "
           "Decision dates and accepted-content hashes are recorded in [review_decisions.json](review_decisions.json).",
           "| Group | Question | Status | Author decision |", "| --- | --- | --- | --- |"]
    for pid, group in status["groups"].items():
        for qid, q in group["questions"].items():
            log.append(f"| {pid} | {qid} | {q['status']} | {q.get('decision') or 'None'} |")
    # Keep the table as one Markdown block.
    docs["REVIEW_LOG.md"] = "\n\n".join(log[:3]) + "\n\n" + "\n".join(log[3:]) + "\n"
    for d in decisions:
        docs["REVIEW_LOG.md"] += (f"\n## {d['decision_id']}: {', '.join(d['approved_problem_ids'])}\n\n"
            + d["author_review_summary_english"] + "\n\n"
            + "Reviewed on: " + d["reviewed_on"] + ".\n")
    docs["REVIEW_LOG.md"] += ("\n## Source qualification, 2026-09-21\n\n" + source_revision["summary"] +
        " "
        "[source_revisions.json](source_revisions.json) records the exact input edits and before/after hashes.\n")
    lines = ["# Primary-source review", "The evidence files preserve original articles, supplements, or primary manuscript text, together with extraction and page images where available. "
             "Numeric records were manually checked at the locations below. Hashes identify these exact files; they do not certify a transcription. "
             "Download URLs, failures, and retained-file status are recorded in `download_log.json`."]
    for s in ss.values():
        lines += [f"## {s['source_id']}", f"[{s['citation']}]({s['url']})", s["version"],
                  "**Checked locations**\n\n" + "\n".join("- " + x for x in s["verified_locations"]),
                  "**Inspection limits**\n\n" + "\n".join("- " + x for x in s["limitations"]),
                  "**Archived files and SHA-256**\n\n" + "\n".join(f"- [{path}]({evidence_link(path)}): `{digest}`" for path, digest in s["local_files"].items())]
    docs["SOURCE_REVIEW.md"] = "\n\n".join(lines) + "\n"
    return docs


if __name__ == "__main__":
    for name, content in documents().items():
        (B / name).write_text(content)
    print("Rendered four review documents from JSON records.")
