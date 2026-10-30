# Scientific Decision Evaluation

[![arXiv](https://img.shields.io/badge/arXiv-2609.24965-b31b1b.svg)](https://arxiv.org/abs/2609.24965)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

Scientific judgment tasks for decision programs: models answer discrete Choice
questions, and deterministic code computes the downstream counts, relations,
and claim labels. The S2 collection contains 20 groups, 40 scientific Choices,
and one engineering Choice. Evaluation reports semantic correctness, complete
downstream outcomes, and final-label correctness separately.

The [thirteen-model analysis](results/s2-thirteen-model-analysis-v1/REPORT.md)
reports the three saved execution cohorts. These are development results on
prepared, source-grounded inputs. Repeated model calls do not establish
unseen-source generalization or calibrated uncertainty.

The paper compares 12 configurations. GLM-5.3-Flash was excluded because 41 of its
50 requests returned HTTP 429 rate-limit errors, leaving only nine complete
responses. Its full execution records and results are retained in the repository.

## Data and results

- [Original cases and Choice definitions](development/s2-nonbio-v1/CHOICES_REVIEW.md)
- [Non-biological expansion](development/s2-nonbio-expansion/batch-001/BATCH_REVIEW.md)
- [Biological expansion](development/s2-biology-expansion/batch-001/BATCH_REVIEW.md)
- [Routing and review coverage](development/s2-execution-v1/COVERAGE.md)
- [Model results](results/s2-thirteen-model-analysis-v1/REPORT.md) and [error analysis](results/s2-thirteen-model-analysis-v1/ERRORS.md)

Inputs and evaluation references are stored separately. Reference answers and
review notes are excluded from model requests. The case records document
preparation, acceptance, and review scope; recorded source-review coverage is listed
in the [coverage table](development/s2-execution-v1/COVERAGE.md).

## Install and verify

Python 3.12 was used. Install the dependencies in an environment of your choice:

```sh
python3 -m pip install -r requirements.txt
python3 -B scripts/verify_release.py
python3 -B scripts/verify_paper_metrics.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -B -m pytest -p no:cacheprovider -p no:capture -q tests
python3 -B development/s2-execution-v1/run.py check
python3 -B development/s2-execution-v2/run.py check
python3 -B development/s2-execution-v3/run.py check
```

Release verification checks the published file hashes and case packages, reparses
all 650 saved S2 requests, and reproduces the scores for 13 models. It makes no
network requests and writes no result files. The execution checks use simulated
responses with network access blocked in tests. See [release contents](RELEASE.md)
for the distinction between published-file hashes and historical manifests.

The [paper-metric check](scripts/verify_paper_metrics.py) reproduces correctness
scores for the paper's 12 configurations and compares each request with the saved
scores. Downstream exactness compares the declared scientific outputs by value
and type, excluding clause judgments and labels. The historical full-outcome and
counts-only checks use different field sets, but give the same pass/fail decisions
on these saved responses. Joint correctness also requires both Choices to match.

## Earlier experiments

The repository also retains the earlier exploratory experiments:

- [Offline graph-score results](results/offline-v1/summary.md)
- [Document eligibility results](results/document-v1/summary.md)
- [Credit diagnostic](results/credit-diagnostic-v1/summary.md)
- [Label-efficiency results](results/label-efficiency-v1/summary.md)
- [Drag comparison](results/drag-sonnet-8192-v1/summary.md) and [resource accounting](results/drag-resource-audit-v1/summary.md)

Reproduce the offline experiments in new output directories:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/offline_pilot.py \
  --output results/offline-reproduction-01
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/label_efficiency.py \
  --output results/label-efficiency-reproduction-01
```

The runners save their configuration, source files, outputs, and local resource
measurements. `--repeats 1` provides a smaller offline check.

## Model execution

The S2 runners are documented in [execution v1](development/s2-execution-v1/README.md),
[execution v2](development/s2-execution-v2/README.md), and
[execution v3](development/s2-execution-v3/README.md). Configuration files preserve
the endpoints and model versions used for the saved experiments.

For the earlier document pilot, configure `OPENROUTER_API_KEY` in your environment
or use the hidden terminal prompt:

```sh
python3 scripts/configure_openrouter.py
python3 scripts/document_pilot.py prepare --output results/document-new
python3 scripts/document_pilot.py run --output results/document-new --limit 4
```

`prepare` is offline; `run` makes paid requests. `.env.local` is ignored and created
with owner-only permissions. Completed attempts, including failures, are retained.
An interrupted request is not silently resent. Existing results can be summarized
without making model calls:

```sh
python3 scripts/document_pilot.py summarize --output results/document-v1
```

## License

Original code and project-authored documentation are licensed under the
[Apache License 2.0](LICENSE).

Third-party papers, figures, and other source materials are excluded from
this license and remain subject to their respective copyright and licensing
terms. Sources are identified in the accompanying case records.
