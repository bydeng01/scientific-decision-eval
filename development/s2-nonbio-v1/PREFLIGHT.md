# S2 non-biological development preflight

2026-09-20 · English revision `s2-nonbio-en-v1`.

The offline rule baseline resolves eleven scientific claims, with D01-O retained as a separate engineering check. Its call matrix contains zero model requests. H01-L/T are program controls because the complete passage supplies both unit mappings.

The English revision translates reviewed source adaptations and updates the text parser while preserving scientific scopes, source IDs, claim quantities, and reference relations. Translation checks are recorded in [LANGUAGE_MIGRATION.json](LANGUAGE_MIGRATION.json); source-review scope is recorded in [ALL_CASES_REVIEW.md](ALL_CASES_REVIEW.md#4-inherited-human-review-and-translation-check).

## Files and execution

| File | Role |
|---|---|
| [inputs/evidence.json](inputs/evidence.json) | Six complete English passages, source IDs and page/table/figure locations |
| [inputs/cases.json](inputs/cases.json) | Twelve claims, target treatments, scope filters and declared quantities |
| [inputs/sources.json](inputs/sources.json) | Five source records, links, types and inherited PDF hashes |
| [evaluation/references.json](evaluation/references.json) | Separate relations, reference counts, labels, actions and D03 fields |
| [evaluation/README.md](evaluation/README.md) | Scoring definitions and denominators |
| [rules.py](rules.py) | Evidence parsing, filtering, deduplication, counting and deterministic decisions |
| [score.py](score.py) | Item-level text scoring and separate human relation oracle |
| [run.py](run.py) | Offline entry point, input snapshots, predictions, resources, matrix and hashes |
| [test_preflight.py](test_preflight.py) | Text, scope, translation, routing, budget and offline regressions |
| [check_counts.py](check_counts.py) | Original eleven oracle-based counting tests |
| [budget.json](budget.json) | Continuing budget and zero call/retry/fallback limits |
| [official_api_check.json](official_api_check.json) | Official API/pricing documentation check; no model selected |
| [LANGUAGE_MIGRATION.json](LANGUAGE_MIGRATION.json) | Language version and preserved-scope audit |

From the repository root:

```bash
python3 development/s2-nonbio-v1/check_counts.py
python3 development/s2-nonbio-v1/test_preflight.py
python3 development/s2-nonbio-v1/run.py
```

The default writes a new `results/s2-nonbio-preflight-en-<UTC timestamp>/` directory. `--output` accepts an alternative new directory; existing results are not overwritten. The only supported mode is `dry-run`; `--mode live` is rejected. The runner loads no credentials, SDK, historical experiment client or network module. Its smoke test disables sockets.

Unsupported evidence is saved as unresolved, receives no scientific label, and makes the runner exit with status 1. It does not trigger a model fallback. Predictions are persisted before references are loaded. The input/code manifest identifies the English revision and records artifact hashes.

Current outputs: [results and routing table](../../results/s2-nonbio-preflight-en-v1/SUMMARY.md), [call matrix](../../results/s2-nonbio-preflight-en-v1/call_matrix.json), [scores](../../results/s2-nonbio-preflight-en-v1/scores.json), [resource summary](../../results/s2-nonbio-preflight-en-v1/resource_summary.json).

## Evidence, preprocessing and scoring

Evidence localization, source adaptation, translation, target selection, scope filters and claim quantities were prepared manually. The English passages retain the explanations that make the relationships explicit. They are translated development passages, not quotations copied from the original papers. Source hashes refer to previously downloaded versions; the sources were not downloaded again for translation.

`extract()` receives only `evidence_text`, `target_treatment` and `scope`. It does not receive case IDs, claim quantities or reference answers. Scope fields encode the already reviewed limits, including selected specimens, columns, operators and rows. The parser requires compatible evidence for these fields. Code compares extracted counts against `declared_counts`; D01-S and D02-S include the additional specimen quantities in their compound claims. Free-text claim extraction remains outside the measured task.

The baseline is a finite phrase grammar developed for these English passages. It matches whole sentences and captures numbers, IDs, temperatures and operators. Each matched sentence and its character offsets are logged. Unknown, missing, negated or conflicting clauses outside the grammar are sent for input/parser review. This outcome is separate from scientific insufficiency.

D03's four sentences describe recorded curing categories, bath temperature control and probing, the 28-day prism group, and an equipment photograph. Parsing them establishes `treatment_level=water_bath_temperature_control`, while `run_boundary` and `specimen_assignment` remain `not_stated`. Without a run-to-specimen mapping, the target count stays null and code requests the missing records. A synthetic added run-record sentence triggers review rather than inheriting the insufficient label.

The human relation oracle bypasses text processing and is stored in `oracle_predictions.jsonl`; text predictions are in `predictions.jsonl`. Scoring checks relation structure, counts, labels and actions separately, plus D03's three fields. D01-O's engineering outcome is excluded from the eleven-claim scientific denominator. The label distribution is five supported, five inconsistent and one insufficient claim.

The six groups come from five sources, with U shared by D01 and D03. Paired claims, translations and repeated executions do not increase the independent-source count. The collection is reviewed development data; unseen-source performance, arbitrary-paper/PDF extraction, model quality and post-record-request outcomes remain unmeasured.

## Routing after the rule baseline

| Group | Relation extracted from evidence | Deterministic work | Residual model question |
|---|---|---|---|
| D01 / S | Half-prisms → prisms → one mixing operation, same curing regimen and 28-day group | Count each level and compare the compound claim | None |
| D01-O | Normal path identifies the mixing unit; simulated candidates omit it | Return `other` in the simulation, stop that branch, complete candidates or transfer | None; engineering simulation only |
| D02 / S | Selected E8-3/Z specimens belong to one complete build | Filter 7/8/9 and deduplicate the parent build | None |
| D03 | Bath control level stated; run boundaries and specimen assignment absent from the parsed material | Unknown count, insufficient label, request records | None |
| C01-T / A | Source-defined whole-plot and subplot units | Count one group or two low-current strips | None |
| H01-L / T | Laser settings apply to columns; heat treatment applies to the whole specimen | Count five columns or one selected whole specimen | None |
| C02 / S | PART IDs identify scars; scan rows identify their operators | Filter six rows, deduplicate 1A/1B; O1-only regression gives one event | None |

Regression probes change case IDs, claim quantities, specimen/column IDs and selected counts. Other checks cover altered D01 scope, C02 operator filtering, missing clauses and unknown language. These are synthetic engineering probes and add no scientific source cases.

## Recorded preflight calls and budget

| Branch | Model/interface | Residual atomic questions | Variants | Model repeats | Base calls | Retry limit | Fallback limit | Maximum attempts including failures | Worst new API cost |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| All twelve current items | None | None | Existing twelve item inputs | 0 | 0 | 0 | 0 | 0 | $0 |

The machine-readable matrix lists each item and its resolved fields. `remaining_atomic_questions` is empty; model and interface are null. Both `model_requests.jsonl` and `model_attempts.jsonl` are empty. Parser review items cannot create a paid batch automatically.

On 2026-09-20, the official OpenRouter documentation was checked for `typesafe/jev-1.13` at `POST https://openrouter.ai/api/alpha/decisions`. Requests use `model`, `state` and `questions`; Choice uses `instructions` and `criteria`, and responses include `answers` and `usage`. The listed price is $0.042 per million input tokens and $0 for output tokens. [Official API](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-questions-and-answers-request), [official pricing](https://openrouter.ai/typesafe/jev-1.13).

TypeSafe's direct documentation lists `jev-1.13.0`, `POST /v1/systemone`, the same input/output prices and SDK backoff retries by default. Direct and OpenRouter context limits are recorded separately in `official_api_check.json`. [TypeSafe Models](https://docs.typesafe.ai/models). This was a documentation check; live connectivity, service tokens and latency were not measured. No comparison-model calls are proposed for already resolved items.

Historical reported/estimated expenditure is **$0.668041116**. The **$1 initial-stage cap** leaves **$0.331958884**; the **$10 total cap** leaves **$9.331958884**. Base calls, failed attempts, retries and fallbacks together have a worst-case additional API cost of **$0**, preserving those balances. Human and local-compute costs are separate unmeasured quantities.

## Source and measurement limits

The saved English offline batch contains only rule-resolved inputs. Its zero-call matrix applies to this preflight, separately from the later S2 execution cohorts.

H's author manuscript still has the 295/285 W discrepancy, which does not affect the current column-ID scope. U's bath-run boundaries and specimen-to-run records remain unaudited. D03's insufficiency answer is conditional on the supplied material and does not establish that the actual study lacked replication.

Logs separate rule-processing wall/CPU time, scoring time, failures, tokens and API cost. Runner timing excludes source localization, human review, translation, rule development, documentation, tests and later record requests. Those times, development tool usage, human and local compute costs, and full-workflow time remain unmeasured. With zero API attempts, the failure count is zero and the failure rate has no denominator.

The English results were recomputed from English inputs. Historical results are retained separately; the pre-translation archive is not included in this release.