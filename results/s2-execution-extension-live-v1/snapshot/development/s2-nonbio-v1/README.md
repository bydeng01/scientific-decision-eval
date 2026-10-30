# S2: treatment units and replication claims

S2 evaluates treatment-unit and replication judgments within the Jev scientific-evaluation project. This directory contains the original offline development cases.

English development materials for the Jev × science pilot. Six case groups contain eleven scientific claims and one engineering routing check, drawn from five non-biological sources. D01 and D03 share a source; paired claims remain grouped by source.

The task checks whether a replication claim agrees with the treatment units established by the supplied evidence. It distinguishes mixing or manufacturing operations, treatment applications, specimens, sub-specimens and repeated measurements. Counts refer to a specified treatment and local scope.

[CHOICES_REVIEW.md](CHOICES_REVIEW.md) contains the complete evidence, claims, fifteen atomic Choice definitions, option descriptions, and author-reviewed references for all twelve items. Per-question decisions are in [REVIEW_LOG.md](choice-review-v1/REVIEW_LOG.md); source-review scope is recorded separately in [ALL_CASES_REVIEW.md](ALL_CASES_REVIEW.md#4-inherited-human-review-and-translation-check). These Choice definitions do not activate calls in this offline runner.

## Run the offline preflight

From the repository root:

```bash
python3 development/s2-nonbio-v1/check_counts.py
python3 development/s2-nonbio-v1/test_preflight.py
python3 development/s2-nonbio-v1/run.py
```

The runner defaults to offline dry-run and writes a new timestamped results directory. Use `--output` to choose a directory that does not yet exist. There is no live mode, credential loading, network client or automatic model fallback.

Read [PREFLIGHT.md](PREFLIGHT.md) for the execution contract and [the English results](../../../../s2-nonbio-preflight-en-v1/SUMMARY.md) for the case-by-case routing table. All current cases are handled by rules; the proposed API batch has zero calls.

## Materials

| File | Contents |
|---|---|
| [ALL_CASES_REVIEW.md](ALL_CASES_REVIEW.md) | Source locations, complete English passages, claims, references and review provenance |
| [inputs/evidence.json](inputs/evidence.json) | Six English evidence passages and their source locations |
| [inputs/cases.json](inputs/cases.json) | Targets, local scope filters, claim text and claim numbers for twelve items |
| [inputs/sources.json](inputs/sources.json) | Five source records, links and inherited PDF hashes |
| [evaluation/references.json](evaluation/references.json) | Separate reference relations, counts, labels and actions |
| [evaluation/README.md](evaluation/README.md) | Scoring definitions and denominators |
| [text_revision.json](text_revision.json) | English revision and translation checks |

## Cases and scope

| Group | Target and scope | Current route |
|---|---|---|
| D01 / D01-S | Mixing conditions; the same mixing operation, same curing regimen and 28-day group | Rule extraction and counting |
| D01-O | D01 with the mixing-batch candidate omitted from a simulated branch | Engineering routing check |
| D02 / D02-S | Complete manufacturing process; E8-3/Z specimens 7, 8, 9 in one build | Rule extraction and counting |
| D03 | Water-bath temperature; the batch's three prisms tested at 28 days | Record control level, leave run count unknown, request records |
| C01-T / C01-A | Fixed temperature/concentration combination; whole-plot group versus low-current strips | Source-defined unit mapping and counting |
| H01-L / H01-T | Default columns 1, 10, 16, 19, 24 in the specimen treated at 870°C | Column-level versus whole-specimen counting |
| C02 / C02-S | Figure 2.6 rows 1–6, 1A/O1 and 1B/O3, pooling operators | Filter and deduplicate wear-scar events |

D03 stores three independent fields: treatment level, run boundary and specimen assignment. Identifying water-bath temperature control alone does not establish a run count. C02 counts two events in the six selected rows; restricting those rows to O1 gives one event. Cutter 1's additional 1C/1D records are outside the scope.

## Input and evaluation boundaries

The English passages translate previously reviewed source adaptations and preserve source locations, targets, scope filters, and claim numbers. [text_revision.json](text_revision.json) records the translation checks. Recorded human confirmations concern the underlying scientific content and scope.

The rule baseline uses a finite phrase grammar written for these development passages. It captures IDs and quantities from the evidence, checks scope, and computes the final labels. Every sentence must be recognized; unsupported text is routed for input/parser review and receives no scientific label. A parsing failure is distinct from an evidence-based `insufficient` answer.

Predictions are written before the reference file is loaded. The manual relation oracle is evaluated separately from text processing. Local aliases such as `batch1`, `prism1` and `sample870` are bookkeeping identifiers; source specimen, column and PART IDs retain their original values.

The results describe reviewed development inputs. They do not measure unseen-source generalization, arbitrary-paper/PDF extraction or model quality. Treatment-unit counts do not establish independence of response errors. Source transcription, input preparation, reference/scoping errors, parser/counting errors, candidate coverage and model errors are tracked as separate issues.

## Resources and open source issues

The historical preflight budget records $0.668041116 in reported/estimated API expenditure against a $10 overall cap and a $1 initial-stage cap, leaving $0.331958884 in that stage. The current call, retry and fallback limits are zero. Runner timings are measured locally; human preparation and translation time, local compute costs, model tokens and full-workflow time are unmeasured.

H's 295/285 W discrepancy remains unresolved and does not affect the column-ID questions. U's water-bath run boundaries and specimen-to-run records remain unaudited. Details and inherited review attribution are retained in [ALL_CASES_REVIEW.md](ALL_CASES_REVIEW.md#4-inherited-human-review-and-translation-check).

This directory reports offline rule evaluation. The earlier drag experiments are retained separately under `results/`.