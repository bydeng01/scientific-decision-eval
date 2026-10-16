# S2 development execution

This package runs the current 20-group S2 collection through code, model Choices and deterministic derivation. It loads the reviewed inputs and evaluation references from their case packages.

The execution configuration is developmental. `budget.cap_usd` is `null`; historical $10/$1 pilot caps do not apply to this package.

## Run from the repository root

Python 3.10 or later and the standard library are sufficient. Commands use `-B` to avoid adding bytecode to the reviewed packages.

```bash
# Read-only source checks, inherited tests and execution-package tests; no API.
python3 -B development/s2-execution-v1/run.py check

# Assemble all requests and run all 300 response fixtures offline.
# Choose a new output path if this directory already exists.
python3 -B development/s2-execution-v1/run.py dry-run --output results/s2-execution-dry-run-next

# Verify the offline run created above and rescore its simulated responses.
python3 -B development/s2-execution-v1/run.py verify --output results/s2-execution-dry-run-next
python3 -B development/s2-execution-v1/run.py score --output results/s2-execution-dry-run-next
```

To prepare a new development experiment:

```bash
# Reports credential presence only; does not contact any service.
python3 -B scripts/configure_science_keys.py --check

# Create a new immutable execution snapshot without making calls.
python3 -B development/s2-execution-v1/run.py prepare --output results/s2-execution-new

# Real calls begin only here. Repeating this command resumes the same run.
python3 -B development/s2-execution-v1/run.py run --output results/s2-execution-new --live

# Rescore after interruption or completion; saved predictions are reparsed first.
python3 -B development/s2-execution-v1/run.py score --output results/s2-execution-new
```

`--limit N` limits new attempts in one invocation and leaves the remaining matrix pending. It does not alter the run's planned denominator. A dry-run directory cannot be promoted to live mode. Local environment variables or the existing owner-only `.env.local` supply `OPENROUTER_API_KEY`, `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`; credentials are never copied into artifacts.

For the distributed historical results, use `python3 -B scripts/verify_release.py`. The `verify` and `score` commands above apply to new runs prepared from the current source files.

## Conditions and scale

| Condition | Work | Model requests |
|---|---|---:|
| `code_only` | Run the inherited six-group parser plus E001/E002/E003/E008 development rules. Leave other semantic questions unresolved. | 0 |
| `model_semantics_plus_code` | Preserve those code routes; submit both Choices of each remaining group together, then derive outcomes in code. | 10 groups × 6 models × 5 repetitions = 300 |
| `reference_oracle` | Supply the accepted answers directly to the same derivation functions to check implementation. | 0 |

There are 21 code-resolved Choices, including D01-O, and 20 model-routed scientific Choices. Each model therefore returns 100 planned scientific answers across five executions. Across all models, the matrix contains 600 semantic answers. [COVERAGE.md](COVERAGE.md) lists every group and Choice.

The code-only condition resolves 20/40 scientific Choices and 15/25 scientific claim outcomes. Its unresolved cases remain visible. Its phrase rules were developed on these passages; their coverage describes this development collection. Model routing identifies the residual semantic contract in this harness, not a proof that no more capable program could resolve it.

The original parser consumes complete clauses. The four new control rules likewise match complete evidence blocks, retain matched text and captures, and fail on an added contradictory clause. E001 uses the explicit regrouping and unit definitions; E002 uses the explicit hourly switch and transition exclusion; E003 uses the stated catalyst reuse; E008 applies full-setting equality. None of these routes makes a model call merely to obtain a count.

## Models and settings

| Local ID | Requested model | Interface | Setting | Input / output USD per million tokens |
|---|---|---|---|---:|
| `jev` | `typesafe/jev-1.13` | OpenRouter Decisions | Native Choice, no provider fallback | 0.042 / 0 |
| `luna` | `gpt-5.6-luna` | OpenAI Responses | medium reasoning | 0.20 / 1.20 |
| `terra` | `gpt-5.6-terra` | OpenAI Responses | medium reasoning | 2 / 12 |
| `sol` | `gpt-5.6-sol` | OpenAI Responses | medium reasoning | 4 / 20 |
| `astra` | `gpt-6-astra` | OpenAI Responses | medium reasoning | 10 / 50 |
| `sonnet` | `claude-sonnet-5` | Anthropic Messages | adaptive thinking, medium effort | 2 / 10 |

The roster preserves the project's Astra and Sonnet comparisons, adds the current OpenAI cost/capability tiers, and includes Jev's documented decision interface. These tiers describe provider positioning and prices; accuracy is to be measured. This matrix compares these specific configurations rather than exhaustive vendor-optimal systems. Official sources and version limits are recorded in [MODEL_SOURCES.md](MODEL_SOURCES.md).

Generative interfaces use a strict JSON schema with one enumerated option ID per question. All systems receive the same evidence, records, instructions and criteria. Generative models also receive an output-format instruction. No tools, temperature, seed, top-p, automatic fallback or reasoning trace request is supplied. Jev probabilities and its distribution-shape confidence are retained as diagnostics; they are not treated as calibrated probabilities shared with the generative models.

The request cap is 32,768 output tokens for reasoning models, including reasoning, and the request-size guard is 98,304 UTF-8 bytes. Jev has no invented output or reasoning parameter. Current requests fit the guard. A 300-second total deadline covers transport and response reading. Concurrency is one to avoid local queueing in this small latency comparison. The prepared seeded schedule shuffles groups and rotates provider order across groups and repetitions.

Five repetitions describe within-input variability and latency spread. There is no majority-vote replacement, power claim, or multiplication of independent source count. Automatic retries and fallbacks are zero, so first-attempt failures remain measurable and an uncertain transport cannot cause duplicate billing. These operating limits follow the measurement design, not an expenditure ceiling.

## Inputs, derivation and scoring

Model packets contain the supplied evidence, target, scope and structured records, followed by the unchanged question text and options. Question keys on the wire are `q1`, `q2`, etc.; the saved map restores repository IDs. The payload omits benchmark claims, reference answers, review rationale, source-revision logs and expected derived outputs. Every provider uses the same source-faithful text and transcribed records; original PDFs and images are provenance assets, not additional model inputs. E005's arithmetic uses the documented Table 3 parameters and does not reconstruct Figure 11 observations.

`dataset.py` and the derivation module do not load evaluation files. Preparation builds requests and code predictions before importing the scoring module. The test suite blocks evaluation-file reads during assembly, injects review canaries, and checks all provider payloads. Source explanations that directly answer a question remain allowed evidence.

`derive.py` implements the original and non-biological mappings and calls the existing biological `derive.py` without modification. Selected semantic relations affect downstream operations; arithmetic, filtering, deduplication, covariance substitution and label composition stay in code. Full-group answer validation precedes derivation. A missing key or invalid option is a response failure, not `not_stated`.

For the expansions, fallback precedence is `conflicting`, then `other`, then `not_stated`. These yield separate review statuses and no composed final label. E004's `partial_identification` is a substantive answer with incomplete provenance, not a format error. The inherited D03 mapping preserves its `insufficient` label and request for run/assignment records; `conflicting_assignment` takes precedence. Biological clause composition retains the existing rule: an inconsistent clause determines the overall label even when another clause has insufficient evidence. B004's unknown germline-line count remains `null`. The same preservation applies to unknown ancestry, mutation origins, powder lots and effective replication.

Reports use fixed denominators:

| Quantity | One repetition | Five repetitions, per model |
|---|---:|---:|
| Model-routed scientific Choices | 20 | 100 |
| Full scientific workflow Choices, including shared code routes | 40 | 200 |
| Scientific claim outcomes | 25 | 125 |
| Recorded source-review subset Choices | 18 | 90 |

D01-O is reported separately. Reusing deterministic results across repeated model workflows does not create additional code observations. Group macro-accuracy gives each of the 20 groups equal weight. The report retains per-Choice, per-claim, per-group and per-repeat results and answer stability. Pending or failed predictions stay in the denominator; partial-run scores are marked provisional. A valid answer can receive Choice credit even if its partner is missing, but incomplete groups have no derived result.

Choice correctness, numeric accounting, complete downstream outputs, final labels, and joint semantic-plus-outcome correctness are reported separately. A wrong Choice can sometimes leave a coarse outcome unchanged. Oracle agreement is an implementation check and is kept outside model performance. Dry-run fixtures select options mechanically and suppress model scores altogether. Structural and arithmetic tests do not replace scientific review. All empirical conclusions from this collection remain development conclusions.

## Saved artifacts and recovery

Each output directory contains:

- `manifest.json`, `config.json`, `plan.json`: source and artifact hashes, Python/platform version, full matrix and exact credential-free request bodies.
- `inputs.json`, `inventory.json`: the complete group/Choice/input join, routes and source families.
- `evaluation_only/`: references, per-Choice mappings, and oracle derivations. These files never enter a request.
- `code_predictions.json`: zero-call answers, evidence matches, derived results and local wall/CPU measurements.
- `snapshot/`: byte copies of code, configuration and source JSON/Markdown. Archived source assets stay at their existing paths and are bound by the manifest.
- `attempts/<job>/intent.json`, `receipt.json`, `prediction.json`: durable request intent, raw HTTP response and parsed answers, failures, derivation and resources.
- `reports/<timestamp>.json`: an immutable scoring snapshot with hashes of attempt artifacts.

Preparation requires a new directory. Running checks the prepared artifacts against current code and inputs; changes require a new run. A process lock prevents two writers. Files are published durably without replacement. A saved receipt is reparsed after interruption. A request intent without a receipt becomes `transport_uncertain` and is never resent automatically. Authentication, request-contract and model-version failures halt the affected model's remaining requests. Other models may continue; the fixed planned matrix remains in the report. Existing predictions are checked against reparsed receipts before reuse or scoring.

Every received response records the requested and served model, response ID, selected headers, raw usage, latency, failure type and any available provider-reported dollar charge. Missing usage or charges remain `null`. Token-price estimates and conservative cache-write upper estimates have separate fields. Known subtotals do not stand in for totals when records are missing. The resource report includes failures and zero retries; local code and scoring time are measured separately. Historical source preparation, human review, implementation, development tool usage, and local compute costs remain unmeasured.

The original run was prepared outside a Git checkout, so its manifest records `git_head` as `null`. SHA-256 manifests and saved source files identify the executed version.

