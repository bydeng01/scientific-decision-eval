# S2 development run: 21 September 2026

The completed run shows near-ceiling Choice accuracy on the current development inputs. Jev, Sol, Astra and Sonnet answered every model-routed Choice correctly. Luna made one semantic error. Terra's two missing answers belong to one interrupted request; its 98 received answers were correct. Jev had the lowest observed request latency and token cost in this configuration.

These results describe a development comparison of the configured services. They provide little separation in semantic accuracy and do not establish unseen-source performance.

## Coverage and completion

The collection contains 20 groups and 41 unique Choices: 40 scientific Choices and one engineering control. Code resolves 20 scientific Choices plus the engineering control without calls. Models handle the remaining 20 scientific Choices in 10 groups. Each of six models has five repetitions: 50 planned requests and 100 semantic answers per model, or 300 requests and 600 semantic answers overall.

The recorded source-review subset covers 18 Choices across 10 groups. Four reviewed Choices use code routes; 14 use model routes. This subset is not the entire collection. Within its 70 repeated model answers per model, Jev/Sol/Astra/Sonnet score 70/70, Luna 69/70 and Terra 68/70.

All 300 planned requests have terminal records. There are 299 HTTP 200 responses and one `InterruptedWithoutReceipt` record, with no pending jobs, retries or fallbacks. The report's `real_api_attempts: 300` counts terminal attempt records; it does not establish 300 completed or billed server calls. Manifest creation to report generation spans 528.853 seconds, including the interruption and restart. Known request latencies sum to 501.296 seconds.

## Accuracy and request latency

The table excludes shared code answers from model accuracy. “Derived exact” covers the 10 model-dependent claim outcomes over five repetitions, with denominator 50. Failed requests remain in the planned denominators.

| Served model | Semantic Choices | Derived exact | Final labels | Median / p95 request seconds |
|---|---:|---:|---:|---:|
| typesafe/jev-1.13-20260917 | 100/100 | 50/50 | 50/50 | 0.335 / 0.442 |
| gpt-5.6-luna | 99/100 | 49/50 | 50/50 | 1.509 / 2.753 |
| gpt-5.6-terra | 98/100 | 49/50 | 49/50 | 1.166 / 2.147 |
| gpt-5.6-sol | 100/100 | 50/50 | 50/50 | 1.385 / 2.370 |
| gpt-6-astra | 100/100 | 50/50 | 50/50 | 2.384 / 4.418 |
| claude-sonnet-5 | 100/100 | 50/50 | 50/50 | 2.162 / 5.422 |

Latency covers the saved HTTP request interval, including transport and service processing. Terra has 49 known intervals; each other model has 50. Jev's median is about 3.5–7.1 times shorter than the other configured services. These are measurements of this serial run and these interfaces, not isolated model compute times.

Four models score 20/20 in each of the five repetitions. Luna scores 20, 19, 20, 20, 20; Terra scores 18, 20, 20, 20, 20 because of the interruption. Only B002-Q01 under Luna varies between valid answer options. Terra's observed-answer score is 98/98, a secondary diagnostic; the primary score remains 98/100.

Code alone resolves 20/40 scientific Choices and 15/25 scientific claim outcomes. The reference oracle reproduces 20/20 group outputs. Oracle agreement checks derivation with supplied answers and is not model accuracy. Adding the shared code routes yields workflow Choice scores of 200/200 for four models, 199/200 for Luna and 198/200 for Terra; these larger denominators should not be used to suggest that each model answered 200 questions.

## The two exceptions

Luna's second B002 repetition selects `separate_then_shared` for B002-Q01 instead of `shared_then_separate`. The supplied evidence says experiment 11a samples one grown culture and experiment 11 uses separately grown cultures. The wrong relation reverses the derived growth-history counts from `{11a: 1, 11: 10}` to `{11a: 10, 11: 1}`. Its answer to B002-Q02 remains correct, so `exact_mutation_origins` stays `null`. The colony totals remain 514 and 624 because those sums do not depend on the disputed relation.

The wrong answer changes the first clause to `consistent`, while the second clause remains `inconsistent`. The composed final label therefore stays `inconsistent`. A label-only metric would hide this error; semantic and complete-outcome scoring detects it.

Terra's first B002 repetition has a durable intent but no saved server response. Recovery marks both Choices `transport_uncertain` and leaves the derived result absent. This is an operationally incomplete observation, not evidence of a scientific misunderstanding or a confirmed provider failure. Its server completion, tokens and charge remain unknown. The run did not resend it.

## Resources and an accounting correction

The original response bodies preserve two fields that the execution normalizer missed:

- `providers.py:118` reads `input_tokens_details.cache_creation_tokens`; all 199 received OpenAI responses instead contain `cache_write_tokens`. Original exact token-price estimates are consequently null, while conservative upper estimates are present.
- `providers.py:120` reads `output_tokens_details.reasoning_tokens`; the 50 Claude responses contain `thinking_tokens`. These sum to 84. They are already included in output-token totals and are not added again for cost.

The analysis script uses those saved fields and the run's price snapshot. Choice and derivation scores are unaffected by these accounting omissions.

| Model | Input tokens | Output tokens | Cache writes | Reasoning / thinking tokens | Cost USD |
|---|---:|---:|---:|---:|---:|
| Jev | 70,875 | 8,330 | unreported | unreported | 0.00297675 reported |
| Luna | 52,290 | 3,173 | 6,180 | 1,783 | 0.010125 estimated |
| Terra | 51,070 known | 1,274 known | 4,963 known | 0 known | 0.0754135 estimated known subtotal |
| Sol | 52,290 | 1,300 | 6,180 | 0 | 0.152348 estimated |
| Astra | 52,290 | 1,300 | 6,180 | 0 | 0.380870 estimated |
| Sonnet | 98,560 | 1,539 | 0 | 84 | 0.212510 estimated |

Each OpenAI model reports 24,720 cached input tokens among its received responses. The revised estimate is `(ordinary input × input rate + cached input × cache-read rate + cache writes × cache-write rate + output × output rate) / 1,000,000`. Anthropic input accounting excludes separately reported cache tokens; both cache quantities are zero here.

The mixed reported/estimated subtotal for 299 received responses is **$0.83424325**. Total billed cost remains unknown because five models do not report dollar charges and the interrupted Terra request has no usage. The original conservative known-response subtotal was $1.38140485; it is not a measured bill. Repeated-input caching is part of this workload. Source preparation, review, implementation and local computing costs are outside these token figures.

## Interpretation

Jev matches the larger configured systems on these inputs while using less observed latency and token cost. The current evidence supports that narrow development result. Five repetitions reuse the same 20 model-routed Choices; they do not produce 100 independent scientific tasks per model. Four perfect scores and one isolated semantic error do not justify a strong capability ranking or statistical superiority claim.

The model-routed references contain no `not_stated`, `other` or `conflicting` answers. Thus this run does not demonstrate when the models can select those fallbacks correctly, despite passing offline handling tests. Downstream unknown values do remain null: the audit checks 179 expected-null fields across the 299 received derivations. All 10 model-dependent reference outcomes reject at least part of their constructed claim, although several retain qualified or insufficient clauses. More varied evidence and claim outcomes would be needed to test broader discrimination.

The inputs are curated source-faithful evidence packets with explicit options, not raw-paper extraction tasks. Near-ceiling performance can reflect this bounded judgment task. Coverage of less explicit evidence and insufficient, conflicting, and supported outcomes remains unmeasured. The analysis accounts for the two usage fields omitted by the execution normalizer.

## Verification and reproduction

The original archive audit verified prepared source/request hashes, reparsed all saved responses, matched all 900 attempt-artifact hashes to the original report, and recomputed all six model score objects exactly. These checks establish integrity and score reproducibility, not a new scientific review. No credential files are read and sockets are disabled.

From the repository root:

```bash
python3 -B scripts/verify_release.py
```

The release verifier checks published files and reproduces saved S2 scores without modifying results. Historical `analyze.py` requires the original archive and its manifests. The source report is `results/s2-execution-live-v1/reports/20260921T063548757325Z.json`; raw evidence for the exceptions is under `attempts/r02-B002-luna/` and `attempts/r01-B002-terra/` in that run directory.
