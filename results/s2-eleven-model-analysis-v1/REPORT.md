# S2: eleven-model development analysis

Both execution cohorts are complete. The five added models preserve the earlier descriptive result: Jev answered all 100 planned semantic Choices correctly and has the lowest observed successful-request median latency and known cost per successful request among these configurations. The extension adds a recurring B002 error under Qwen Max, HTTP 429 failures on three router configurations, and a fifth model with a perfect fixed-denominator score, Claude Opus 5.

The new results sharpen the distinction between semantic accuracy, complete derived outputs and service availability. They add little breadth to the scientific evidence: all seven observed semantic errors across eleven models concern the same Choice, B002-Q01. Five repetitions reuse 20 unique model-routed Choices in 10 groups.

## Completion and audit

Cohort A is the original six-model run, from 2026-09-21 06:26:59.989 to 06:35:48.494 UTC. It contains 300 terminal records: 299 HTTP 200 responses and one `InterruptedWithoutReceipt` record. Cohort B is the five-model extension, from 07:04:57.928 to 07:43:31.100 UTC: 250 terminal records, 239 HTTP 200 responses and 11 HTTP 429 responses. These intervals run from first intent to last recorded receipt. Both cohorts have zero pending intents, zero unstarted jobs, zero retries and zero fallbacks.

The original archive audit reparsed all 550 saved receipts and regenerated their predictions with the appropriate version of the execution package. It matched all 1,650 attempt-file hashes to the historical reports and reproduced all eleven score objects. Manifest checks covered 149 source files and 78 prepared artifacts in A, and 151 source files and 80 prepared artifacts in B. Inputs, references, evidence packets and question maps agree across cohorts; `dataset.py`, `derive.py` and `scoring.py` are byte-identical. Code predictions and reference-oracle outputs were also rederived. Neither original manifest records a Git commit because the runs were prepared outside a Git checkout; file hashes and saved source snapshots identify the executed versions.

The 2026-09-21 audit checked a 995-file pre-extension baseline and 1,979 protected files, including both run directories, source snapshots and the earlier analysis. Those hashes identify the original archive. Current published-file hashes and verification instructions are in [RELEASE.md](../../RELEASE.md). B004 and E010 retain their approved source qualifications; integrity checks do not extend independent scientific review.

## Choice accuracy and downstream results

The full collection contains 20 groups, 40 scientific Choices and one engineering control. Code resolves 20 scientific Choices plus the control; models answer the other 20 scientific Choices. Each model therefore has 100 planned semantic answers and 50 model-dependent derived outcomes over five repetitions. The primary score retains failed requests in those fixed denominators. “Observed” is a secondary diagnostic over received valid answers, with potentially different coverage.

| Model | Cohort | Choice /100 | Observed Choice | Derived /50 | Labels /50 | Semantic errors | Failed requests |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Jev 1.13 | A | 100/100 | 100/100 | 50/50 | 50/50 | 0 | 0 |
| GPT-5.6 Luna | A | 99/100 | 99/100 | 49/50 | 50/50 | 1 | 0 |
| GPT-5.6 Terra | A | 98/100 | 98/98 | 49/50 | 49/50 | 0 | 1 |
| GPT-5.6 Sol | A | 100/100 | 100/100 | 50/50 | 50/50 | 0 | 0 |
| GPT-6 Astra | A | 100/100 | 100/100 | 50/50 | 50/50 | 0 | 0 |
| Claude Sonnet 5 | A | 100/100 | 100/100 | 50/50 | 50/50 | 0 | 0 |
| Qwen3.8 Flash | B | 83/100 | 83/84 | 41/50 | 42/50 | 1 | 8 |
| Qwen3.8 Max 0902 | B | 95/100 | 95/100 | 45/50 | 50/50 | 5 | 0 |
| DeepSeek V4.1 Flash | B | 96/100 | 96/96 | 48/50 | 48/50 | 0 | 2 |
| DeepSeek V4 Pro 0813 | B | 98/100 | 98/98 | 49/50 | 49/50 | 0 | 1 |
| Claude Opus 5 | B | 100/100 | 100/100 | 50/50 | 50/50 | 0 | 0 |

There are 1,076 valid semantic answers: 1,069 correct and seven wrong. Another 24 planned answers are absent because of 12 operationally unresolved or failed requests. All 538 HTTP 200 responses satisfy the saved format and provider/model contracts. There are zero malformed responses, invalid options or missing answer fields within those successful responses. The 11 HTTP 429 responses account for 22 missing answers; Terra's uncertain interruption accounts for two. None is a `not_stated` semantic answer.

Across configurations, complete model-dependent outcomes score 531/550 and final labels 538/550. All 538 received outcomes have the expected final label, including the seven semantically wrong cases. These pooled counts describe the recorded workload, not 1,100 independent scientific tests. Counts-only exactness equals full-outcome exactness for every model in this run; the complete field-by-field projections are in `outcomes.json`.

Shared code alone resolves 20/40 scientific Choices and 15/25 scientific outcomes. The reference oracle reproduces 20/20 group outputs with supplied answers. Neither quantity measures model capability. The audit confirms that 322 expected-null fields remain null in the received model-dependent derivations, including unknown ancestry, mutation origins, parent lots, effective replication and validated germline lines.

## Repeat stability and the B002 failure

Every repeat has a fixed semantic denominator of 20. “All five correct” counts unique Choices that were received and correct in all five repetitions. The reviewed-subset column uses only the 14 model-routed Choices in the recent review, giving 70 repeated answers; the full recent review has 18 Choices, including four code-routed Choices.

| Model | R1 /20 | R2 /20 | R3 /20 | R4 /20 | R5 /20 | All five correct /20 | Reviewed subset /70 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Jev 1.13 | 20 | 20 | 20 | 20 | 20 | 20 | 70/70 |
| GPT-5.6 Luna | 20 | 19 | 20 | 20 | 20 | 19 | 69/70 |
| GPT-5.6 Terra | 18 | 20 | 20 | 20 | 20 | 18 | 68/70 |
| GPT-5.6 Sol | 20 | 20 | 20 | 20 | 20 | 20 | 70/70 |
| GPT-6 Astra | 20 | 20 | 20 | 20 | 20 | 20 | 70/70 |
| Claude Sonnet 5 | 20 | 20 | 20 | 20 | 20 | 20 | 70/70 |
| Qwen3.8 Flash | 19 | 14 | 14 | 16 | 20 | 5 | 59/70 |
| Qwen3.8 Max 0902 | 19 | 19 | 19 | 19 | 19 | 19 | 65/70 |
| DeepSeek V4.1 Flash | 20 | 20 | 20 | 20 | 16 | 16 | 68/70 |
| DeepSeek V4 Pro 0813 | 20 | 20 | 20 | 20 | 18 | 18 | 68/70 |
| Claude Opus 5 | 20 | 20 | 20 | 20 | 20 | 20 | 70/70 |

B002-Q01 asks whether experiment 11a samples one grown culture and experiment 11 samples separately grown cultures. Its reference is `shared_then_separate`, giving growth histories `{11a: 1, 11: 10}`. The saved scope and table identifiers supply this association. Luna R2 and Qwen Flash R1 choose the reverse. Qwen Max chooses `both_shared`, `both_shared`, `separate_then_shared`, `both_separate`, `separate_then_shared` across its five repeats: zero correct B002-Q01 answers and three different wrong options. Its other 19 Choices are correct in every repeat.

These answers change growth-history counts to `{1,1}`, `{10,1}` or `{10,10}`. All seven cases answer B002-Q02 correctly as `clonal_descendants`, retain unknown mutation origins as null, and retain colony totals 514 and 624. The second claim clause remains inconsistent, so the composed final label stays inconsistent. This is a concrete reason to score semantic decisions and full derived outputs alongside labels.

Only Luna, Qwen Flash and Qwen Max vary between valid answer options, each on B002-Q01. Terra and the two DeepSeek models have stable correct received answers but incomplete repeat coverage. Qwen Flash's 83/100 includes one semantic error and 16 absent answers; Qwen Max's 95/100 contains five semantic errors with complete coverage. Their fixed-denominator ordering should not be read as a pure semantic-capability ranking. The exact seven errors, their changed outputs, and all 12 operational exceptions appear in [ERRORS.md](ERRORS.md).

## Tokens, cache and cost

The table reports saved-usage totals over successful responses. A row with fewer than 50 successes is a known subtotal, including any displayed zero. Unreported fields remain null. OpenAI and router prompt-token totals include their cache quantities; Anthropic reports ordinary input separately from cache reads and writes, which are zero here. Tokenizers and response formats differ: Jev returns probability information as well as Choices.

| Model | Usage records | Input | Output | Cache read | Cache write | Reasoning / thinking | USD | Cost basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jev 1.13 | 50 | 70,875 | 8,330 | unreported | unreported | unreported | 0.00297675 | reported |
| GPT-5.6 Luna | 50 | 52,290 | 3,173 | 24,720 | 6,180 | 1,783 | 0.010125 | estimated |
| GPT-5.6 Terra | 49 | 51,070 | 1,274 | 24,720 | 4,963 | 0 | 0.0754135 | estimated; subtotal |
| GPT-5.6 Sol | 50 | 52,290 | 1,300 | 24,720 | 6,180 | 0 | 0.152348 | estimated |
| GPT-6 Astra | 50 | 52,290 | 1,300 | 24,720 | 6,180 | 0 | 0.38087 | estimated |
| Claude Sonnet 5 | 50 | 98,560 | 1,539 | 0 | 0 | 84 | 0.21251 | estimated |
| Qwen3.8 Flash | 42 | 43,306 | 30,437 | 29,440 | 0 | 29,339 | 0.01685633 | reported; subtotal |
| Qwen3.8 Max 0902 | 50 | 49,635 | 28,485 | 16,384 | 0 | 27,463 | 0.241508 | reported |
| DeepSeek V4.1 Flash | 48 | 54,872 | 19,654 | 38,528 | 0 | 18,661 | 0.016837016 | reported; subtotal |
| DeepSeek V4 Pro 0813 | 49 | 58,705 | 23,727 | 2,654 | 0 | 22,678 | 0.168063016 | reported; subtotal |
| Claude Opus 5 | 50 | 98,560 | 1,681 | 0 | 0 | 226 | 0.534825 | estimated |

The original six-model subtotal remains **$0.834243250**. The extension adds **$0.978089362**: $0.443264362 reported by the router and $0.534825 estimated for Opus from saved usage. Combined, the accounting contains **$0.446241112 in server-reported charges across 239 responses**, plus **$1.366091500 in estimates for 299 other responses**, giving **$1.812332612 for 538 known responses**. The alternative all-usage estimate has the same subtotal; it is a cross-check, not an additional charge.

Total cost for all 550 planned requests remains unknown. No usage or charge is saved for Terra's interruption or the 11 rate-limit responses, and a 429 is not assigned a zero charge. Direct OpenAI and Anthropic results provide usage-based estimates rather than billed dollar totals. Server-reported dollars also remain distinct from an independently reconciled invoice. `summary.json` and `requests.json` retain reported values, token estimates, coverage and unknown totals separately.

The original normalizer omitted OpenAI `input_tokens_details.cache_write_tokens` and Claude `output_tokens_details.thinking_tokens`. This analysis uses those saved fields and matches the earlier six-model reconciliation. It does not substitute zero for the old report's missing cache fields. Input estimates apply ordinary, cache-read and cache-write prices separately; Anthropic's separately reported cache inputs are added to ordinary input. All prices come from the execution snapshots, with no online price refresh.

The four added router configurations report roughly 95–96% of output tokens as reasoning. Output totals already include those tokens, so they are billed once. Sonnet and Opus report 84 and 226 thinking tokens respectively; Terra, Sol and Astra report zero reasoning tokens in their received responses, and Jev does not report that field. Configured `medium` or `high` effort and reported token categories do not establish equal internal computation. Cache-read fractions also differ substantially: about 68% for Qwen Flash, 33% for Qwen Max, 70% for DeepSeek Flash and 4.5% for DeepSeek Pro among received prompt tokens. Resource results describe this repeated-input workload.

## Request latency

Latency is the saved client request interval, including transport and service processing. Median uses the ordinary sample median; p95 uses nearest rank, `ceil(0.95*n)`. The primary latency column uses successful responses. The all-terminal column includes known error-response intervals and is supplied to reconcile the historical reports. Terra has one unknown interval. A and B were measured in separate execution windows and cannot establish a simultaneous service-speed ranking.

| Model | Cohort | Success n | Success median / p95 s | All known median / p95 s | Known USD / success |
| --- | --- | --- | --- | --- | --- |
| Jev 1.13 | A | 50 | 0.335 / 0.442 | 0.335 / 0.442 | 0.00005954 |
| GPT-5.6 Luna | A | 50 | 1.509 / 2.753 | 1.509 / 2.753 | 0.00020250 |
| GPT-5.6 Terra | A | 49 | 1.166 / 2.147 | 1.166 / 2.147 | 0.00153905 |
| GPT-5.6 Sol | A | 50 | 1.385 / 2.370 | 1.385 / 2.370 | 0.00304696 |
| GPT-6 Astra | A | 50 | 2.384 / 4.418 | 2.384 / 4.418 | 0.00761740 |
| Claude Sonnet 5 | A | 50 | 2.162 / 5.422 | 2.162 / 5.422 | 0.00425020 |
| Qwen3.8 Flash | B | 42 | 14.182 / 34.320 | 13.452 / 34.320 | 0.00040134 |
| Qwen3.8 Max 0902 | B | 50 | 14.236 / 21.393 | 14.236 / 21.393 | 0.00483016 |
| DeepSeek V4.1 Flash | B | 48 | 5.449 / 8.821 | 5.416 / 8.821 | 0.00035077 |
| DeepSeek V4 Pro 0813 | B | 49 | 7.569 / 10.086 | 7.281 / 10.086 | 0.00342986 |
| Claude Opus 5 | B | 50 | 3.237 / 3.967 | 3.237 / 3.967 | 0.01069650 |

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
