"""Small, synthetic document eligibility pilot through OpenRouter.

prepare freezes cases and requests. run sends them with a bounded spend ledger.
Raw responses and failures are retained; no automatic retries or JSON repairs.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    "openai/gpt-4.1-mini": {"prompt": 0.4, "completion": 1.6},
    "anthropic/claude-haiku-4.5": {"prompt": 1.0, "completion": 5.0},
}
RULES = """Fictional document eligibility policy POL-01, evaluated on 2026-09-01.
Only records matching the current applicant ID count. A signed section is
authoritative; draft sections and applicant statements are not. For route and
prior-award verification separately, use the latest dated signed section.
is_renewal: the authoritative route is RENEWAL, rather than FIRST-TIME.
renewal_ok: the authoritative prior-award verification says ACTIVE and its
renewal signature is PRESENT. REVOKED, EXPIRED, or PENDING signature fails.
new_ok: the current applicant has at least 24 completed, non-transfer credits.
Use the final signed credit ledger. Planned and transfer rows do not count.
Duplicate rows with the same course ID count once; all duplicates here agree.
Eligibility rule: if is_renewal, use renewal_ok; otherwise use new_ok.
The unused route's evidence has no effect on eligibility. This task evaluates
document sufficiency under this policy, not any real-world benefit or entitlement.
"""
FIELDS = ("is_renewal", "renewal_ok", "new_ok")


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+"\n")


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line] if path.exists() else []


def gold(record):
    aid = record["applicant_id"]
    route = max((r for r in record["routes"] if r["applicant"] == aid and r["signed"]), key=lambda r:r["date"])
    prior = max((r for r in record["prior"] if r["applicant"] == aid and r["signed"]), key=lambda r:r["date"])
    counted = {r["course"]:r["credits"] for r in record["ledger"]
               if r["applicant"] == aid and r["status"] == "COMPLETED" and not r["transfer"]}
    bits = [route["route"] == "RENEWAL", prior["status"] == "ACTIVE" and prior["signature"] == "PRESENT", sum(counted.values()) >= 24]
    return dict(zip(FIELDS, map(int, bits))), int(bits[1] if bits[0] else bits[2])


def cases():
    output = []
    for family in ("plain", "superseded", "other_applicant", "credit_exclusions"):
        for index, bits in enumerate(itertools.product((0, 1), repeat=3)):
            renewal, prior_ok, new_ok = bits
            aid = f"AP-{100+index}"
            route = "RENEWAL" if renewal else "FIRST-TIME"
            opposite = "FIRST-TIME" if renewal else "RENEWAL"
            record = dict(applicant_id=aid,
                routes=[dict(applicant=aid, date="2026-08-30", signed=True, route=route)],
                prior=[dict(applicant=aid, date="2026-08-30", signed=True,
                            status="ACTIVE" if prior_ok else "REVOKED", signature="PRESENT")],
                ledger=[dict(applicant=aid, course="C101", credits=12, status="COMPLETED", transfer=False),
                        dict(applicant=aid, course="C102", credits=12 if new_ok else 11, status="COMPLETED", transfer=False)])
            if family == "superseded":
                record["routes"].insert(0, dict(applicant=aid, date="2026-08-01", signed=True, route=opposite))
                record["routes"].append(dict(applicant=aid, date="2026-09-01", signed=False, route=opposite))
                record["prior"].insert(0, dict(applicant=aid, date="2026-08-01", signed=True,
                                             status="REVOKED" if prior_ok else "ACTIVE", signature="PRESENT"))
            if family == "other_applicant":
                record["routes"].append(dict(applicant="AP-999", date="2026-09-01", signed=True, route=opposite))
                record["prior"].append(dict(applicant="AP-999", date="2026-09-01", signed=True,
                                           status="REVOKED" if prior_ok else "ACTIVE", signature="PRESENT"))
                record["ledger"].append(dict(applicant="AP-999", course="C900", credits=100, status="COMPLETED", transfer=False))
            if family == "credit_exclusions":
                record["ledger"] += [record["ledger"][1].copy(),
                    dict(applicant=aid, course="C103", credits=12, status="PLANNED", transfer=False),
                    dict(applicant=aid, course="C104", credits=12, status="COMPLETED", transfer=True)]
                if not prior_ok:
                    record["prior"][-1].update(status="ACTIVE", signature="PENDING")
            lines = [f"Current applicant: {aid}. Document packet for fictional grant POL-01."]
            for r in record["routes"]:
                lines.append(f"Route notice: applicant {r['applicant']}; {r['date']}; {'SIGNED' if r['signed'] else 'DRAFT, UNSIGNED'}; route {r['route']}.")
            for r in record["prior"]:
                lines.append(f"Prior-award verification: applicant {r['applicant']}; {r['date']}; SIGNED; status {r['status']}; renewal signature {r['signature']}.")
            lines.append("Final SIGNED credit ledger follows. Each line is a ledger row, not an additional award.")
            for r in record["ledger"]:
                lines.append(f"Applicant {r['applicant']}, course {r['course']}, {r['credits']} credits, {r['status']}, {'TRANSFER' if r['transfer'] else 'NON-TRANSFER'}.")
            labels, eligible = gold(record)
            assert list(labels.values()) == list(bits)
            output.append(dict(id=f"{family}-{index}", family=family, document="\n".join(lines),
                               record=record, labels=labels, eligible=eligible, split="development"))
    return output


def request_payload(model, mode, document):
    names = FIELDS if mode == "nodes" else ("eligible",)
    instruction = ("Estimate the probability that each named predicate in the policy is true. "
                   "Return all three probabilities; do not substitute the final eligibility decision."
                   if mode == "nodes" else
                   "Apply the complete eligibility rule. Estimate the probability that this packet is eligible.")
    return dict(model=model, temperature=0, max_tokens=400,
        provider=dict(require_parameters=True, allow_fallbacks=False, sort="price", max_price=MODELS[model]),
        messages=[dict(role="system", content="Evaluate the supplied fictional document under the exact policy. "
                       "Return only the requested JSON. Numbers are probabilities between zero and one.\n"+RULES),
                  dict(role="user", content=instruction+"\n\nDOCUMENT\n"+document)],
        response_format=dict(type="json_schema", json_schema=dict(name="document_probabilities", strict=True,
            schema=dict(type="object", properties={name:dict(type="number") for name in names},
                        required=list(names), additionalProperties=False))))


def reserve_cost(payload):
    # Input bytes plus 1024 tokens for framing/schema overhead is intentionally
    # conservative for these text-only requests. Output cap includes all tokens.
    input_allowance = len(json.dumps(payload).encode()) + 1024
    price = MODELS[payload["model"]]
    return (input_allowance * price["prompt"] + payload["max_tokens"]*price["completion"])/1e6


def prepare(out):
    out.mkdir(parents=True, exist_ok=False)
    items = cases()
    (out/"cases.jsonl").write_text("".join(json.dumps(c, ensure_ascii=False)+"\n" for c in items))
    plans = []
    # No conversation state is carried between requests or examples.
    for case, model, mode in itertools.product(items, MODELS, ("nodes", "direct")):
        payload = request_payload(model, mode, case["document"])
        plans.append(dict(id=f"{case['id']}::{model}::{mode}", case_id=case["id"], model=model,
                          mode=mode, payload=payload, reserve_usd=reserve_cost(payload)))
    (out/"requests.jsonl").write_text("".join(json.dumps(p)+"\n" for p in plans))
    save_json(out/"manifest.json", dict(created_utc=datetime.now(timezone.utc).isoformat(),
        budget_usd=1.0, scope="synthetic development-only smoke test", cases=len(items), requests=len(plans),
        models=MODELS, max_reserved_usd=sum(p["reserve_usd"] for p in plans),
        sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/"cases.jsonl", out/"requests.jsonl", Path(__file__))}))
    print(f"Prepared {len(items)} cases, {len(plans)} requests; conservative reservation ${sum(p['reserve_usd'] for p in plans):.4f}.")


def load_key():
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        path = ROOT/".env.local"
        for line in path.read_text().splitlines() if path.exists() else []:
            if line.startswith("OPENROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("\"'")
    if not key:
        raise SystemExit("No key configured. Run scripts/configure_openrouter.py in your terminal.")
    return key


def validate_response(response, mode):
    choice = response["choices"][0]
    if choice.get("finish_reason") != "stop":
        raise ValueError("Completion did not finish normally")
    parsed = json.loads(choice["message"]["content"])
    names = FIELDS if mode == "nodes" else ("eligible",)
    if not isinstance(parsed, dict) or set(parsed) != set(names):
        raise ValueError("Unexpected output keys")
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in parsed.values()):
        raise ValueError("Invalid probability")
    return parsed


def run(out, limit):
    key = load_key()
    pending = out/"pending_request.json"
    if pending.exists():
        raise SystemExit("An earlier request has an uncertain outcome. Inspect the pending record before resuming; it will not be resent.")
    manifest = json.loads((out/"manifest.json").read_text())
    for name in ("cases.jsonl", "requests.jsonl"):
        if hashlib.sha256((out/name).read_bytes()).hexdigest() != manifest["sha256"][name]:
            raise SystemExit(f"Frozen input changed: {name}")
    with urllib.request.urlopen("https://openrouter.ai/api/v1/models", timeout=30) as response:
        catalog = json.load(response)
    relevant = [m for m in catalog["data"] if m["id"] in MODELS]
    save_json(out/"model_catalog.json", relevant)
    if len(relevant) != len(MODELS) or any("structured_outputs" not in m["supported_parameters"] for m in relevant):
        raise SystemExit("Requested structured-output model is unavailable")
    existing = read_jsonl(out/"responses.jsonl")
    done = {r["id"] for r in existing}
    charged = sum(r["budget_charge_usd"] for r in existing)
    plans = [p for p in read_jsonl(out/"requests.jsonl") if p["id"] not in done]
    with (out/"responses.jsonl").open("a") as stream:
        for plan in plans[:limit] if limit else plans:
            if charged + plan["reserve_usd"] > manifest["budget_usd"]:
                print("Stopped at spend limit.", flush=True); break
            request = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(plan["payload"]).encode(),
                headers={"Authorization":"Bearer "+key, "Content-Type":"application/json"})
            row = dict(id=plan["id"], case_id=plan["case_id"], model=plan["model"], mode=plan["mode"],
                       started_utc=datetime.now(timezone.utc).isoformat(), reserve_usd=plan["reserve_usd"])
            # A crash must not turn an uncertain request into an automatic retry.
            with pending.open("x") as pending_stream:
                json.dump(row, pending_stream)
            start = time.monotonic()
            try:
                with urllib.request.urlopen(request, timeout=55) as response:
                    row["raw_response"] = json.load(response)
                row["probabilities"] = validate_response(row["raw_response"], plan["mode"])
                row["status"] = "valid"
            except urllib.error.HTTPError as error:
                row.update(status="http_error", http_status=error.code,
                           error_body=error.read().decode(errors="replace").replace(key, "[REDACTED]"))
            except Exception as error:
                row.update(status="invalid_or_transport_error", error=str(error).replace(key, "[REDACTED]"))
            row["elapsed_seconds"] = time.monotonic()-start
            usage_cost = row.get("raw_response", {}).get("usage", {}).get("cost")
            row["reported_cost_usd"] = float(usage_cost) if isinstance(usage_cost, (int,float)) else None
            row["budget_charge_usd"] = row["reported_cost_usd"] if row["reported_cost_usd"] is not None else row["reserve_usd"]
            charged += row["budget_charge_usd"]
            stream.write(json.dumps(row, allow_nan=False)+"\n"); stream.flush()
            pending.unlink()
            print(f"{plan['id']}: {row['status']}; accounted ${charged:.5f}", flush=True)
            if row["status"] != "valid":
                print("Stopped after failure; raw attempt retained. No automatic retry.", flush=True); break
    summarize(out)


def summarize(out):
    import numpy as np
    from scipy.stats import beta
    from sklearn.metrics import roc_auc_score
    from offline_pilot import certificate_bound, error_distribution, BITS, program
    cases_by_id = {c["id"]:c for c in read_jsonl(out/"cases.jsonl")}
    responses = read_jsonl(out/"responses.jsonl")
    analyses = []
    for model in MODELS:
        for mode in ("nodes", "direct"):
            rows = [r for r in responses if r["model"] == model and r["mode"] == mode and r["status"] == "valid"]
            for r in rows:
                case = cases_by_id[r["case_id"]]
                if mode == "nodes":
                    p = np.array([r["probabilities"][f] for f in FIELDS])
                    bits = (p >= .5).astype(int); q = np.maximum(p, 1-p)
                    action = int(program(bits, "routed"))
                    scores = dict(uniform=float(1-q.min()),
                                  graph_certificate=certificate_bound(bits,q,"routed"),
                                  graph_independent=float(np.sum(error_distribution(q,"independent")*(program(bits^BITS,"routed") != action))))
                    node_errors = {f:int(bits[i] != case["labels"][f]) for i,f in enumerate(FIELDS)}
                else:
                    p = r["probabilities"]["eligible"]; action = int(p >= .5)
                    scores = dict(direct=1-max(p,1-p)); node_errors = None
                analyses.append(dict(case_id=r["case_id"], family=case["family"], model=model, mode=mode,
                                     action=action, gold=case["eligible"], error=int(action != case["eligible"]),
                                     node_errors=node_errors, scores=scores))
    save_json(out/"analysis.json", analyses)
    lines = ["# Document development pilot", "", "32 controlled fictional packets, four templates, eight predicate combinations per template.",
             "Every case is development data. Template-related examples are not independent draws from a deployment population.",
             "No thresholds were calibrated or certified on this batch. Probabilities are model-generated scores.", "",
             "| Model | Mode | Valid / attempted | Terminal errors | Score | Brier error score | Error AUROC |",
             "|---|---|---:|---:|---|---:|---:|"]
    for model, mode in itertools.product(MODELS, ("nodes", "direct")):
        group = [r for r in analyses if r["model"]==model and r["mode"]==mode]
        attempted = sum(r["model"]==model and r["mode"]==mode for r in responses)
        if not group:
            lines.append(f"| {model} | {mode} | 0/{attempted} | — | — | — | — |"); continue
        errors = np.array([r["error"] for r in group])
        for score in group[0]["scores"]:
            s = np.array([r["scores"][score] for r in group])
            auc = f"{roc_auc_score(errors,s):.4f}" if len(np.unique(errors))==2 else "undefined (one class)"
            lines.append(f"| {model} | {mode} | {len(group)}/{attempted} | {errors.sum()} | {score} | {np.mean((s-errors)**2):.5f} | {auc} |")
    actual = sum(r["reported_cost_usd"] or 0 for r in responses)
    charged = sum(r["budget_charge_usd"] for r in responses)
    lines += ["", f"Reported API cost: ${actual:.6f}. Budget accounting including unknown-cost attempts: ${charged:.6f} of $1.", "",
              "Undefined error AUROC means this batch contains only correct or only incorrect predictions; it cannot establish error discrimination.",
              "Brier values for union/product scores are diagnostics, not a claim that these scores are calibrated probabilities.",
              "A zero-error development batch is not evidence that the deployment error is zero. Even 32 independent zero-error observations for a fixed policy would have a one-sided 95% upper bound of "
              f"{beta.ppf(.95,1,32):.4f}; the template design here does not justify that binomial interval."]
    (out/"summary.md").write_text("\n".join(lines)+"\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("prepare", "run", "summarize"))
    parser.add_argument("--output", type=Path, default=ROOT/"results/document-v1")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    if args.mode == "prepare": prepare(args.output)
    elif args.mode == "run": run(args.output, args.limit)
    else: summarize(args.output)


if __name__ == "__main__": main()
