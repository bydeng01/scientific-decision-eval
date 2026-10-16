"""Post-inspection diagnostic: transcribe ledger, then perform arithmetic in code."""

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path

from document_pilot import MODELS, ROOT, read_jsonl, reserve_cost, run, save_json

IDS = ("plain-0", "plain-1", "plain-7", "superseded-0", "superseded-5",
       "other_applicant-0", "credit_exclusions-0", "credit_exclusions-1")
PARENT = ROOT/"results/document-v1"


def credits(extraction):
    seen = {}
    for row in extraction["entries"]:
        key = (row["applicant"], row["course"])
        value = (row["credits"], row["completed"], row["transfer"])
        if key in seen and seen[key] != value:
            raise ValueError("Conflicting duplicate course rows")
        seen[key] = value
    return sum(value[0] for (applicant, course), value in seen.items()
               if applicant == extraction["applicant_id"] and value[1] and not value[2])


def payload(model, document):
    entry = dict(type="object", properties=dict(applicant=dict(type="string"), course=dict(type="string"),
                 credits=dict(type="integer"), completed=dict(type="boolean"), transfer=dict(type="boolean")),
                 required=["applicant", "course", "credits", "completed", "transfer"], additionalProperties=False)
    return dict(model=model, temperature=0, max_tokens=1000,
        provider=dict(require_parameters=True, allow_fallbacks=False, sort="price", max_price=MODELS[model]),
        messages=[dict(role="system",content="Transcribe the current applicant identifier and every row in the final signed credit ledger. "
                       "Include duplicate rows, other applicants, planned rows, and transfer rows exactly as stated. "
                       "COMPLETED means completed=true; PLANNED means false. NON-TRANSFER means transfer=false. "
                       "Do not calculate totals or make any eligibility decision. Return only the requested JSON."),
                  dict(role="user",content=document)],
        response_format=dict(type="json_schema",json_schema=dict(name="ledger",strict=True,
            schema=dict(type="object",properties=dict(applicant_id=dict(type="string"),
                entries=dict(type="array",items=entry)),required=["applicant_id","entries"],additionalProperties=False))))


def prepare(out):
    out.mkdir(parents=True, exist_ok=False)
    items = [c for c in read_jsonl(PARENT/"cases.jsonl") if c["id"] in IDS]
    (out/"cases.jsonl").write_text("".join(json.dumps(c)+"\n" for c in items))
    plans = []
    for case, model in itertools.product(items, MODELS):
        p = payload(model,case["document"])
        plans.append(dict(id=f"{case['id']}::{model}::ledger",case_id=case["id"],model=model,
                          mode="ledger",payload=p,reserve_usd=reserve_cost(p)))
    (out/"requests.jsonl").write_text("".join(json.dumps(p)+"\n" for p in plans))
    parent_cost = sum(r["budget_charge_usd"] for r in read_jsonl(PARENT/"responses.jsonl"))
    save_json(out/"manifest.json",dict(created_utc=datetime.now(timezone.utc).isoformat(),
        budget_usd=1-parent_cost, parent_cost_usd=parent_cost, scope="post-inspection diagnostic on exposed cases",
        cases=len(items), requests=len(plans), max_reserved_usd=sum(p["reserve_usd"] for p in plans),
        sha256={str(p.relative_to(out)) if p.is_relative_to(out) else str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (out/"cases.jsonl",out/"requests.jsonl",Path(__file__),ROOT/"scripts/document_pilot.py")}))
    print(f"Prepared {len(plans)} diagnostic requests; reserved ${sum(p['reserve_usd'] for p in plans):.4f}.")


def summarize(out):
    cases = {c["id"]:c for c in read_jsonl(out/"cases.jsonl")}
    originals = {(r["case_id"],r["model"]):r for r in read_jsonl(PARENT/"responses.jsonl") if r["mode"]=="nodes" and r["status"]=="valid"}
    analyses = []
    lines = ["# Targeted credit diagnostic", "", "These eight cases were selected after inspecting document-v1. They are exposed development cases.", "",
             "| Model | Case | Exact transcription | Code credits | Gold new_ok | Original error | Revised error |",
             "|---|---|---|---:|---:|---:|---:|"]
    raw = read_jsonl(out/"responses.jsonl")
    for row in raw:
        if row["status"] != "valid":
            continue
        case = cases[row["case_id"]]; old = originals[(row["case_id"],row["model"])]["probabilities"]
        expected = [dict(applicant=r["applicant"],course=r["course"],credits=r["credits"],
                         completed=r["status"]=="COMPLETED",transfer=r["transfer"]) for r in case["record"]["ledger"]]
        def canonical(entries): return sorted(json.dumps(e,sort_keys=True) for e in entries)
        extracted = row["probabilities"]
        exact = canonical(expected)==canonical(extracted["entries"]) and extracted["applicant_id"]==case["record"]["applicant_id"]
        total = credits(extracted)
        old_action = int(old["renewal_ok"]>=.5 if old["is_renewal"]>=.5 else old["new_ok"]>=.5)
        new_action = int(old["renewal_ok"]>=.5 if old["is_renewal"]>=.5 else total>=24)
        result = dict(case_id=row["case_id"],model=row["model"],exact_transcription=exact,code_credits=total,
                      gold_new_ok=case["labels"]["new_ok"],original_error=int(old_action!=case["eligible"]),
                      revised_error=int(new_action!=case["eligible"]))
        analyses.append(result)
        lines.append(f"| {row['model']} | {row['case_id']} | {exact} | {total} | {result['gold_new_ok']} | {result['original_error']} | {result['revised_error']} |")
    spent = sum(r["budget_charge_usd"] for r in raw)
    parent_cost = json.loads((out/"manifest.json").read_text())["parent_cost_usd"]
    lines += ["",f"Diagnostic accounted cost: ${spent:.6f}; total including original batch: ${spent+parent_cost:.6f}.",
              "Any reduction here concerns an exposed, selected subset. The unchanged original route/renewal predictions can still cause terminal errors. No risk certificate is claimed."]
    save_json(out/"analysis.json",analyses)
    (out/"summary.md").write_text("\n".join(lines)+"\n")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("prepare","run","summarize"))
    parser.add_argument("--output",type=Path,default=ROOT/"results/credit-diagnostic-v1")
    args=parser.parse_args()
    if args.mode=="prepare": prepare(args.output)
    elif args.mode=="run":
        run(args.output,0,analyze=False)
        summarize(args.output)
    else: summarize(args.output)


if __name__=="__main__": main()
