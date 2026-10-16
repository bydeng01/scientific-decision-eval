# S2: thirteen-model development analysis

All three cohorts are complete. The final GLM/Kimi report was generated at 2026-09-21 08:21:55 UTC. There are no pending intents or unstarted jobs. Kimi adds a sixth model with 100/100 correct planned semantic answers. GLM has 41 HTTP 429 responses out of 50 attempts: its 18/100 fixed-denominator score records 18 correct received answers and 82 absent answers, not 82 scientific mistakes.

The additions preserve Jev's lowest observed successful-request median latency and known per-success cost with perfect coverage on these development packets. They broaden model coverage without adding scientific questions.

## Completion and integrity

| Cohort | Planned | Terminal | HTTP 200 | HTTP 429 | Uncertain | First intent UTC | Last receipt UTC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 300 | 300 | 299 | 0 | 1 | 2026-09-21T06:26:59.988791+00:00 | 2026-09-21T06:35:48.493868+00:00 |
| B | 250 | 250 | 239 | 11 | 0 | 2026-09-21T07:04:57.927522+00:00 | 2026-09-21T07:43:31.100331+00:00 |
| C | 100 | 100 | 59 | 41 | 0 | 2026-09-21T08:10:54.107497+00:00 | 2026-09-21T08:21:55.110316+00:00 |

A contains the original six models, B the five-model extension, and C GLM and Kimi. There were no retries or fallbacks. Terra's original interruption remains an unknown server outcome. The 52 received rate-limit responses remain operational failures. All 597 HTTP 200 responses satisfy the existing format and model/provider contracts; there are zero format errors and zero missing answer fields within these successful responses.

The original archive audit verified all manifests, reparsed 650 saved receipts, matched 1,950 attempt-file hashes, and reproduced all 13 historical model score objects. Inputs, reference answers, packets and question maps agree across all cohorts. The shared dataset, derivation and scoring code is byte-identical. Code outputs and the reference oracle were regenerated, and 356 expected-null fields were preserved in received model-dependent derivations. The original manifests record no Git HEAD because the runs were prepared outside a Git checkout; saved snapshots and hashes identify the versions.

The 2026-09-21 audit checked 2,390 protected files, including the eleven-model analysis and the 1,994-file pre-GLM/Kimi baseline. Those hashes identify the original archive. Current published-file hashes and verification instructions are in [RELEASE.md](../../RELEASE.md). Integrity and scoring checks do not constitute a new scientific source audit.

## Choice and derived-outcome scores

The collection contains 20 groups, 40 scientific Choices and one engineering control. Code resolves 20 scientific Choices plus the control. Models answer the other 20 Choices in 10 groups. Each model has five repetitions: 100 planned semantic answers and 50 model-dependent outcomes. The primary fixed denominators include absent answers; the observed-answer score is secondary and can have selective coverage. Shared code and oracle accuracy are not model capability.

| Model | Cohort | Choice /100 | Observed Choice | Full derived /50 | Labels /50 | Semantic errors | Failed requests |
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
| GLM-5.3-Flash | C | 18/100 | 18/18 | 9/50 | 9/50 | 0 | 41 |
| Kimi K3 | C | 100/100 | 100/100 | 50/50 | 50/50 | 0 | 0 |

Across the recorded workload, 1,187/1,300 planned semantic answers are correct, 7 are wrong, and 106 are absent. Of the 650 model-dependent outcomes, 590 match the full reference and 597 match its final label. These are workload totals, not independent scientific sample sizes. All seven known semantic errors remain on B002-Q01: Luna R2, Qwen Flash R1, and Qwen Max R1–R5. Each changes culture-history counts while leaving the final label unchanged. No additional semantic error appears in the two new models. Counts-only exactness equals full-outcome exactness for every model.

Kimi achieves 100/100 semantic, 50/50 full derived and 50/50 label scores. GLM achieves 18/18 received semantic answers and 9/9 received full outcomes. Its fixed scores are 18/100 and 9/50 because of the 41 rate limits; neither its low fixed score nor its perfect received-answer score establishes its capability over the complete task set.

## Five-repeat stability

Each repeat has a denominator of 20 semantic answers. The last column counts unique Choices received and correct in all five repeats.

| Model | R1 /20 | R2 /20 | R3 /20 | R4 /20 | R5 /20 | All five correct /20 |
| --- | --- | --- | --- | --- | --- | --- |
| Jev 1.13 | 20 | 20 | 20 | 20 | 20 | 20 |
| GPT-5.6 Luna | 20 | 19 | 20 | 20 | 20 | 19 |
| GPT-5.6 Terra | 18 | 20 | 20 | 20 | 20 | 18 |
| GPT-5.6 Sol | 20 | 20 | 20 | 20 | 20 | 20 |
| GPT-6 Astra | 20 | 20 | 20 | 20 | 20 | 20 |
| Claude Sonnet 5 | 20 | 20 | 20 | 20 | 20 | 20 |
| Qwen3.8 Flash | 19 | 14 | 14 | 16 | 20 | 5 |
| Qwen3.8 Max 0902 | 19 | 19 | 19 | 19 | 19 | 19 |
| DeepSeek V4.1 Flash | 20 | 20 | 20 | 20 | 16 | 16 |
| DeepSeek V4 Pro 0813 | 20 | 20 | 20 | 20 | 18 | 18 |
| Claude Opus 5 | 20 | 20 | 20 | 20 | 20 | 20 |
| GLM-5.3-Flash | 16 | 2 | 0 | 0 | 0 | 0 |
| Kimi K3 | 20 | 20 | 20 | 20 | 20 | 20 |

GLM provides no valid answers in repeats 3–5, so its five-repeat semantic stability is unmeasured. Kimi returns the reference answer for all 20 Choices in every repeat. The only variability between valid answer options remains B002-Q01 for Luna, Qwen Flash and Qwen Max. Qwen Max returns three different wrong options across its five attempts.

The recorded source-review subset covers 18 Choices, including 14 of the 20 model-routed Choices. E004-Q01/Q02, E005-Q01/Q02 and E009-Q01/Q02 are outside that review subset. Their references remain the existing development references; this audit neither rejects nor independently validates them. Per-Choice answers, errors and review flags are in [choices.json](choices.json); full output comparisons are in [outcomes.json](outcomes.json).

## Tokens, cache and cost

Values below are known subtotals over saved successful responses. A row with fewer than 50 responses has incomplete usage coverage, including when an observed subtotal is zero. Missing fields remain null. Reasoning/thinking tokens are included in output tokens and are not charged twice. OpenAI and router input totals include cache quantities; Anthropic ordinary input is reported separately.

| Model | Usage n | Input | Output | Cache read | Cache write | Reasoning/thinking | Known USD | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jev 1.13 | 50 | 70,875 | 8,330 | unreported | unreported | unreported | 0.002976750 | reported |
| GPT-5.6 Luna | 50 | 52,290 | 3,173 | 24,720 | 6,180 | 1,783 | 0.010125000 | estimated |
| GPT-5.6 Terra | 49 | 51,070 | 1,274 | 24,720 | 4,963 | 0 | 0.075413500 | estimated |
| GPT-5.6 Sol | 50 | 52,290 | 1,300 | 24,720 | 6,180 | 0 | 0.152348000 | estimated |
| GPT-6 Astra | 50 | 52,290 | 1,300 | 24,720 | 6,180 | 0 | 0.380870000 | estimated |
| Claude Sonnet 5 | 50 | 98,560 | 1,539 | 0 | 0 | 84 | 0.212510000 | estimated |
| Qwen3.8 Flash | 42 | 43,306 | 30,437 | 29,440 | 0 | 29,339 | 0.016856330 | reported |
| Qwen3.8 Max 0902 | 50 | 49,635 | 28,485 | 16,384 | 0 | 27,463 | 0.241508000 | reported |
| DeepSeek V4.1 Flash | 48 | 54,872 | 19,654 | 38,528 | 0 | 18,661 | 0.016837016 | reported |
| DeepSeek V4 Pro 0813 | 49 | 58,705 | 23,727 | 2,654 | 0 | 22,678 | 0.168063016 | reported |
| Claude Opus 5 | 50 | 98,560 | 1,681 | 0 | 0 | 226 | 0.534825000 | estimated |
| GLM-5.3-Flash | 9 | 8,831 | 601 | 0 | 0 | 423 | 0.001625150 | reported |
| Kimi K3 | 50 | 60,450 | 13,688 | 41,984 | 0 | 12,347 | 0.273313200 | reported |

Cohort C adds $0.274938350 in server-reported charges: $0.001625150 for GLM's nine successes and $0.273313200 for Kimi's 50 successes. The combined known subtotal is $2.087270962, comprising $0.721179462 reported for 298 responses and $1.366091500 estimated from usage for 299 other responses. Total cost for all 650 attempts remains unknown because 53 operational exceptions have no saved usage/charge. A 429 is not assigned a zero charge; no number here is an independently reconciled invoice total. Usage estimates cross-check reported costs and are not added to them.

The original six-model cost reconciliation remains unchanged. Raw cache-write and thinking fields omitted by the original normalizer are retained here rather than replaced by zero. Prices come from saved execution configurations. Kimi reports 41,984 cached input tokens out of 60,450 prompt tokens and 12,347 reasoning tokens out of 13,688 output tokens; GLM reports zero cache reads over its nine received responses. These workloads therefore do not represent equal cache or internal-compute conditions.

## Latency

Latency is the saved client request interval. The primary column includes successes; the secondary column includes all known terminal intervals. p95 uses nearest rank. All three cohorts were executed in separate time windows. GLM's success p95 uses only nine responses and equals its largest observed success interval.

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
| GLM-5.3-Flash | C | 9 | 1.821 / 5.288 | 0.534 / 3.574 | 0.00018057 |
| Kimi K3 | C | 50 | 11.116 / 25.744 | 11.116 / 25.744 | 0.00546626 |

GLM's short 429 responses reduce its all-terminal median to 0.534 seconds, compared with 1.821 seconds for successes. Kimi's successful median/p95 is 11.116/25.744 seconds. Jev retains the lowest observed success median (0.335 seconds) and known cost per successful request ($0.000059535). These are descriptive measurements of the recorded routes, settings, cache use and execution windows, not a simultaneous comparison or intrinsic model-speed ranking.

## Reproduction

From the repository root:

```bash
python3 -B scripts/verify_release.py
```

The release verifier checks published-file hashes, reparses the saved responses, and reproduces all thirteen model score objects without modifying results. The historical `verify_analysis.py` requires the original private archive. Changed source data require a new analysis directory. [summary.json](summary.json) holds aggregate results; [requests.json](requests.json) holds response-level resources and hashes; [ERRORS.md](ERRORS.md) lists exceptions; `audit-*.json` and `rescored-*.json` hold cohort audit evidence and reproduced scores. [verification.json](verification.json) records the original archive reproduction checks.
