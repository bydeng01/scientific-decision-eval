"""Render the audited JSON as project reports, without changing past artifacts."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = json.loads((HERE / "summary.json").read_text())
REQUESTS = json.loads((HERE / "requests.json").read_text())
CHOICES = json.loads((HERE / "choices.json").read_text())
OUTCOMES = json.loads((HERE / "outcomes.json").read_text())
ORDER = ["jev", "luna", "terra", "sol", "astra", "sonnet", "qwen_flash", "qwen_max", "deepseek_flash", "deepseek_pro", "opus5"]
NAMES = dict(zip(ORDER, ["Jev 1.13", "GPT-5.6 Luna", "GPT-5.6 Terra", "GPT-5.6 Sol", "GPT-6 Astra", "Claude Sonnet 5",
                       "Qwen3.8 Flash", "Qwen3.8 Max 0902", "DeepSeek V4.1 Flash", "DeepSeek V4 Pro 0813", "Claude Opus 5"]))


def frac(x):
    return f'{x["correct"]}/{x["denominator"]}'


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
                     + ["| " + " | ".join(map(str, row)) + " |" for row in rows])


def pair(x):
    return f'{x["median"]:.3f} / {x["p95_nearest_rank"]:.3f}' if x["median"] is not None else "unknown"


def tokens(x):
    v = x["known_subtotal"]
    return f"{v:,}" if v is not None else "unreported"


def write(name, value):
    p = HERE / name
    if p.exists():
        assert p.read_text() == value, f"Report differs: use a new directory ({name})"
    else:
        with p.open("x") as f:
            f.write(value)


quality = []
resource_rows = []
latency_rows = []
repeat_rows = []
for mid in ORDER:
    m = S["models"][mid]
    quality.append([NAMES[mid], "A" if m["cohort"] == "original" else "B", frac(m["semantic_fixed"]),
                    frac(m["semantic_observed_secondary"]), frac(m["model_dependent_outcomes_exact"]),
                    frac(m["model_dependent_labels_exact"]), m["choice_categories"].get("semantic_error", 0),
                    m["failed_requests"]])
    r, c = m["resources"], m["cost"]
    cost = c["selected_reported_else_estimated"]["known_subtotal"]
    basis = "reported" if c["server_reported"]["known_records"] else "estimated"
    if m["failed_requests"]:
        basis += "; subtotal"
    resource_rows.append([NAMES[mid], m["successful_requests"], tokens(r["input_tokens"]), tokens(r["output_tokens"]),
                          tokens(r["cached_input_tokens"]), tokens(r["cache_write_tokens"]),
                          tokens(r["reasoning_or_thinking_tokens"]), f"{cost:.9f}".rstrip("0"), basis])
    latency_rows.append([NAMES[mid], "A" if m["cohort"] == "original" else "B", m["successful_requests"],
                         pair(m["latency_successful"]), pair(m["latency_all_terminal"]),
                         f'{c["known_cost_per_successful_request"]:.8f}'])
    repeat_rows.append([NAMES[mid], *[r["semantic_fixed"]["correct"] for r in m["per_repeat"]],
                        m["all_five_correct_questions"], frac(m["reviewed_model_subset"])])

report = """# S2: eleven-model development analysis

Both execution cohorts are complete. The five added models preserve the earlier descriptive result: Jev answered all 100 planned semantic Choices correctly and has the lowest observed successful-request median latency and known cost per successful request among these configurations. The extension adds a recurring B002 error under Qwen Max, HTTP 429 failures on three router configurations, and a fifth model with a perfect fixed-denominator score, Claude Opus 5.

The new results sharpen the distinction between semantic accuracy, complete derived outputs and service availability. They add little breadth to the scientific evidence: all seven observed semantic errors across eleven models concern the same Choice, B002-Q01. Five repetitions reuse 20 unique model-routed Choices in 10 groups.

## Completion and audit

Cohort A is the original six-model run, from 2026-09-21 06:26:59.989 to 06:35:48.494 UTC. It contains 300 terminal records: 299 HTTP 200 responses and one `InterruptedWithoutReceipt` record. Cohort B is the five-model extension, from 07:04:57.928 to 07:43:31.100 UTC: 250 terminal records, 239 HTTP 200 responses and 11 HTTP 429 responses. These intervals run from first intent to last recorded receipt. Both cohorts have zero pending intents, zero unstarted jobs, zero retries and zero fallbacks.

The original archive audit reparsed all 550 saved receipts and regenerated their predictions with the appropriate version of the execution package. It matched all 1,650 attempt-file hashes to the historical reports and reproduced all eleven score objects. Manifest checks covered 149 source files and 78 prepared artifacts in A, and 151 source files and 80 prepared artifacts in B. Inputs, references, evidence packets and question maps agree across cohorts; `dataset.py`, `derive.py` and `scoring.py` are byte-identical. Code predictions and reference-oracle outputs were also rederived. Neither original manifest records a Git commit because the runs were prepared outside a Git checkout; file hashes and saved source snapshots identify the executed versions.

The 2026-09-21 audit checked a 995-file pre-extension baseline and 1,979 protected files, including both run directories, source snapshots and the earlier analysis. Those hashes identify the original archive. Current published-file hashes and verification instructions are in [RELEASE.md](../../RELEASE.md). B004 and E010 retain their approved source qualifications; integrity checks do not extend independent scientific review.

## Choice accuracy and downstream results

The full collection contains 20 groups, 40 scientific Choices and one engineering control. Code resolves 20 scientific Choices plus the control; models answer the other 20 scientific Choices. Each model therefore has 100 planned semantic answers and 50 model-dependent derived outcomes over five repetitions. The primary score retains failed requests in those fixed denominators. “Observed” is a secondary diagnostic over received valid answers, with potentially different coverage.

""" + table(["Model", "Cohort", "Choice /100", "Observed Choice", "Derived /50", "Labels /50", "Semantic errors", "Failed requests"], quality) + """

There are 1,076 valid semantic answers: 1,069 correct and seven wrong. Another 24 planned answers are absent because of 12 operationally unresolved or failed requests. All 538 HTTP 200 responses satisfy the saved format and provider/model contracts. There are zero malformed responses, invalid options or missing answer fields within those successful responses. The 11 HTTP 429 responses account for 22 missing answers; Terra's uncertain interruption accounts for two. None is a `not_stated` semantic answer.

Across configurations, complete model-dependent outcomes score 531/550 and final labels 538/550. All 538 received outcomes have the expected final label, including the seven semantically wrong cases. These pooled counts describe the recorded workload, not 1,100 independent scientific tests. Counts-only exactness equals full-outcome exactness for every model in this run; the complete field-by-field projections are in `outcomes.json`.

Shared code alone resolves 20/40 scientific Choices and 15/25 scientific outcomes. The reference oracle reproduces 20/20 group outputs with supplied answers. Neither quantity measures model capability. The audit confirms that 322 expected-null fields remain null in the received model-dependent derivations, including unknown ancestry, mutation origins, parent lots, effective replication and validated germline lines.

## Repeat stability and the B002 failure

Every repeat has a fixed semantic denominator of 20. “All five correct” counts unique Choices that were received and correct in all five repetitions. The reviewed-subset column uses only the 14 model-routed Choices in the recent review, giving 70 repeated answers; the full recent review has 18 Choices, including four code-routed Choices.

""" + table(["Model", "R1 /20", "R2 /20", "R3 /20", "R4 /20", "R5 /20", "All five correct /20", "Reviewed subset /70"], repeat_rows) + """

B002-Q01 asks whether experiment 11a samples one grown culture and experiment 11 samples separately grown cultures. Its reference is `shared_then_separate`, giving growth histories `{11a: 1, 11: 10}`. The saved scope and table identifiers supply this association. Luna R2 and Qwen Flash R1 choose the reverse. Qwen Max chooses `both_shared`, `both_shared`, `separate_then_shared`, `both_separate`, `separate_then_shared` across its five repeats: zero correct B002-Q01 answers and three different wrong options. Its other 19 Choices are correct in every repeat.

These answers change growth-history counts to `{1,1}`, `{10,1}` or `{10,10}`. All seven cases answer B002-Q02 correctly as `clonal_descendants`, retain unknown mutation origins as null, and retain colony totals 514 and 624. The second claim clause remains inconsistent, so the composed final label stays inconsistent. This is a concrete reason to score semantic decisions and full derived outputs alongside labels.

Only Luna, Qwen Flash and Qwen Max vary between valid answer options, each on B002-Q01. Terra and the two DeepSeek models have stable correct received answers but incomplete repeat coverage. Qwen Flash's 83/100 includes one semantic error and 16 absent answers; Qwen Max's 95/100 contains five semantic errors with complete coverage. Their fixed-denominator ordering should not be read as a pure semantic-capability ranking. The exact seven errors, their changed outputs, and all 12 operational exceptions appear in [ERRORS.md](ERRORS.md).

## Tokens, cache and cost

The table reports saved-usage totals over successful responses. A row with fewer than 50 successes is a known subtotal, including any displayed zero. Unreported fields remain null. OpenAI and router prompt-token totals include their cache quantities; Anthropic reports ordinary input separately from cache reads and writes, which are zero here. Tokenizers and response formats differ: Jev returns probability information as well as Choices.

""" + table(["Model", "Usage records", "Input", "Output", "Cache read", "Cache write", "Reasoning / thinking", "USD", "Cost basis"], resource_rows) + """

The original six-model subtotal remains **$0.834243250**. The extension adds **$0.978089362**: $0.443264362 reported by the router and $0.534825 estimated for Opus from saved usage. Combined, the accounting contains **$0.446241112 in server-reported charges across 239 responses**, plus **$1.366091500 in estimates for 299 other responses**, giving **$1.812332612 for 538 known responses**. The alternative all-usage estimate has the same subtotal; it is a cross-check, not an additional charge.

Total cost for all 550 planned requests remains unknown. No usage or charge is saved for Terra's interruption or the 11 rate-limit responses, and a 429 is not assigned a zero charge. Direct OpenAI and Anthropic results provide usage-based estimates rather than billed dollar totals. Server-reported dollars also remain distinct from an independently reconciled invoice. `summary.json` and `requests.json` retain reported values, token estimates, coverage and unknown totals separately.

The original normalizer omitted OpenAI `input_tokens_details.cache_write_tokens` and Claude `output_tokens_details.thinking_tokens`. This analysis uses those saved fields and matches the earlier six-model reconciliation. It does not substitute zero for the old report's missing cache fields. Input estimates apply ordinary, cache-read and cache-write prices separately; Anthropic's separately reported cache inputs are added to ordinary input. All prices come from the execution snapshots, with no online price refresh.

The four added router configurations report roughly 95–96% of output tokens as reasoning. Output totals already include those tokens, so they are billed once. Sonnet and Opus report 84 and 226 thinking tokens respectively; Terra, Sol and Astra report zero reasoning tokens in their received responses, and Jev does not report that field. Configured `medium` or `high` effort and reported token categories do not establish equal internal computation. Cache-read fractions also differ substantially: about 68% for Qwen Flash, 33% for Qwen Max, 70% for DeepSeek Flash and 4.5% for DeepSeek Pro among received prompt tokens. Resource results describe this repeated-input workload.

## Request latency

Latency is the saved client request interval, including transport and service processing. Median uses the ordinary sample median; p95 uses nearest rank, `ceil(0.95*n)`. The primary latency column uses successful responses. The all-terminal column includes known error-response intervals and is supplied to reconcile the historical reports. Terra has one unknown interval. A and B were measured in separate execution windows and cannot establish a simultaneous service-speed ranking.

""" + table(["Model", "Cohort", "Success n", "Success median / p95 s", "All known median / p95 s", "Known USD / success"], latency_rows) + """

The Qwen Flash 429 responses have a median of 5.470 seconds, DeepSeek Flash's 0.337 seconds and DeepSeek Pro's 0.566 seconds. Including them lowers the apparent request median without producing an answer. Jev's observed median of 0.335 seconds remains below every added configuration, and its known $0.000059535 per successful request remains lowest after accounting for incomplete response counts. These are descriptive comparisons across the recorded cohorts and routes.

Within cohort B, Opus has the shortest successful-response median, 3.237 seconds, and complete correct coverage, while DeepSeek Flash has the lowest known cost per success, about $0.00035077, with two HTTP failures. The latter's received answers are all correct. Qwen Max costs more per successful request than Qwen Flash and has a recurring error; these observations do not support a monotonic price–quality or size–latency relation. They also do not identify whether model architecture, reasoning settings, provider scheduling or cache behavior caused the resource differences.

## Scope and limitations

The study evaluates 20 model-routed Choices in 10 development groups. Repeated requests and additional models do not increase the number of distinct questions. All seven semantic errors concern B002-Q01 and retain the reference final label. The recorded source-review subset covers 18 scientific Choices, including 14 of the 20 model-routed Choices.

None of the model-routed reference answers is `not_stated`, `other` or `conflicting`, and every model-dependent reference claim rejects at least one clause. These results do not measure held-out-source generalization, calibrated abstention, or performance on supported and boundary cases. Fallback and null-preservation checks establish code behavior only.

Operational measurements describe the recorded cohorts, which used different execution windows, routes, cache conditions and reasoning settings. The response-level measurements exclude human source localization, adaptation, candidate construction, review, implementation and local computation. They do not establish total-workflow savings or isolate the causal benefit of the code/model decomposition.

## Reproduction and files

From the repository root, using Python 3.10 or later:

```bash
python3 -B scripts/verify_release.py
python3 -B results/s2-eleven-model-analysis-v1/render_report.py
```

The release verifier checks the published files and reproduces saved model scores from the recorded responses. The renderer checks that this report matches the saved analysis JSON. Historical `analyze.py` and `verify_analysis.py` require the original archive and its manifests.

- [summary.json](summary.json): model scores, repetitions, per-Choice stability, resource coverage and accounting totals.
- [requests.json](requests.json), [choices.json](choices.json), [outcomes.json](outcomes.json): 550 request rows, 1,100 model Choice rows and 550 full model-dependent outcome comparisons.
- [audit-original.json](audit-original.json) and [audit-extension.json](audit-extension.json): manifest and hash evidence, completion state and raw-response reconciliation.
- [rescored-original.json](rescored-original.json) and [rescored-extension.json](rescored-extension.json): fresh offline score objects matching the historical reports. Full-workflow scores inside these files retain their original labels and are separate from model-only scores.
- [protected-sha256.json](protected-sha256.json): files checked by the original audit; [ERRORS.md](ERRORS.md): exact failures and B002 output changes.

Historical reports: [cohort A](../s2-execution-live-v1/reports/20260921T063548757325Z.json), [cohort B](../s2-execution-extension-live-v1/reports/20260921T074331334719Z.json). Requested model IDs and saved served identities are retained in `summary.json`. The four added router models returned their accepted named model IDs and fixed Alibaba or Fireworks provider; Opus returned `claude-opus-5` through direct Anthropic. Those identifiers are service observations, not immutable weight hashes. Opus 4.8 is absent.
"""
write("REPORT.md", report)

bad = [c for c in CHOICES if c["category"] == "semantic_error"]
error_rows = []
for c in bad:
    o = next(o for o in OUTCOMES if o["job_id"] == c["job_id"])
    r = next(r for r in REQUESTS if r["job_id"] == c["job_id"])
    counts = o["actual"]["counts"]["growth_histories"]
    link = "../../" + r["receipt_path"]
    error_rows.append([f'[{c["job_id"]}]({link})', c["prediction"], f'{counts["11a"]} / {counts["11"]}',
                       o["actual"]["clauses"]["independent_histories_11a"], o["actual"]["final_label"]])
failure_rows = []
for r in REQUESTS:
    if r["status"] == "complete":
        continue
    link = "../../" + r["receipt_path"]
    failure_rows.append([f'[{r["job_id"]}]({link})', r["http_status"] if r["http_status"] is not None else "no response",
                         r["transport_error"] or r["limit_source"], 2, "unknown"])
errors = """# S2 semantic and operational exceptions

All seven observed semantic errors concern B002-Q01. The expected option is `shared_then_separate`, and expected culture growth histories are `11a: 1; 11: 10`. The correct final label is `inconsistent`. Links point to the saved response receipt; the same attempt directory contains the request intent and persisted prediction.

""" + table(["Attempt", "Selected option", "Growth histories 11a / 11", "First clause", "Final label"], error_rows) + """

All seven retain `clonal_descendants` for B002-Q02, `exact_mutation_origins: null`, and colony totals `{11a: 514, 11: 624}`. The second clause, `one_colony_one_origin`, is inconsistent in every case. It keeps the final label correct despite the wrong Choice and derived counts. These are seven responses to one independent question, not seven independent scientific cases.

The operational exceptions contain no valid Choice answers. Each removes two planned answers and one complete derived outcome while remaining in the fixed denominators.

""" + table(["Attempt", "HTTP status", "Saved error category", "Absent answers", "Usage / cost"], failure_rows) + """

Terra's interruption is a terminal local recovery record with unknown server completion, tokens and charge. It is not a confirmed semantic error or a confirmed provider rejection. Every extension failure is a received HTTP 429. The router identifies the fixed upstream provider's shared pool as the rate-limit source: eight Alibaba/Qwen Flash, two Fireworks/DeepSeek Flash and one Fireworks/DeepSeek Pro. This is the saved service explanation; no further upstream diagnosis was performed. No absent record is converted into `not_stated`, and no failed request is retried or replaced.

Format/contract errors and missing answer fields within HTTP 200 responses both count zero. All remaining received semantic answers match their existing references. See [choices.json](choices.json) for every Choice and [outcomes.json](outcomes.json) for complete actual/reference projections, including nulls.
"""
write("ERRORS.md", errors)
print("REPORT.md and ERRORS.md reproduced from audited JSON")
