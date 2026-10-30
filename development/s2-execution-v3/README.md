# S2: GLM and Kimi extension

This third execution cohort adds GLM-5.3-Flash and Kimi K3 to the existing eleven-model comparison. It uses the same ten model-routed groups: E004, E005, E006, E007, E009, E010 and B001–B004. Each group has two semantic Choices, and each model has five repetitions: 50 requests, 100 semantic answers and 50 model-dependent outcomes per model. The new batch totals 100 requests and 200 semantic answers.

| Local ID | Requested model | Fixed OpenRouter provider | Catalog quantization | Effort |
|---|---|---|---|---|
| glm_flash | z-ai/glm-5.3-flash | Fireworks (`fireworks`) | unknown | high |
| kimi_k3 | moonshotai/kimi-k3 | Moonshot AI (`moonshotai/mxfp4`) | mxfp4 | high |

The saved catalog names model versions 20260826 and 20260715. Fireworks lists strict structured outputs for GLM; the Z.AI endpoint lists JSON response formatting without the `structured_outputs` capability. The selected Moonshot AI endpoint lists both. Both accept the inherited 32,768-token output envelope. Requests require supported parameters, disable provider fallback, and validate the returned model and provider. Quantization values come from endpoint metadata; weights were not inspected.

Both models document `low`, `high` and `max` effort; this cohort requests `high`, the middle available setting. The prior cohorts use their recorded settings. Internal computation is not matched across these interface settings. No external tools are enabled. The request interval has a 300-second total deadline, with serial execution, zero automatic retries and zero fallbacks. Rate-limit errors and ambiguous interruptions remain in the planned denominator.

## Run from the repository root

The recorded cohort is in `results/s2-execution-glm-kimi-live-v1`. Use a new directory for another run; preparation is offline and `--live` makes paid requests.

```bash
python3 -B development/s2-execution-v3/run.py prepare --output results/s2-execution-glm-kimi-new
python3 -B development/s2-execution-v3/run.py run --output results/s2-execution-glm-kimi-new --live
```

Supply an OpenRouter key through the environment or the local credential helper. The live command runs these two models, reads the key internally and prints request-start and request-finish events. If the process has stopped, rerunning the same command continues unstarted jobs; received failures and uncertain intents are retained rather than retried. Only one process may hold the run lock.

The run writes a new report automatically. The following commands verify or rescore saved files without model calls:

```bash
python3 -B development/s2-execution-v3/run.py verify --output results/s2-execution-glm-kimi-new
python3 -B development/s2-execution-v3/run.py score --output results/s2-execution-glm-kimi-new
```

For the distributed historical results, run `python3 -B scripts/verify_release.py`. The commands above use a new directory prepared from the current source files.

## Reproduce preparation checks

```bash
python3 -B development/s2-execution-v3/run.py check
```

The new contract tests disable networking and credential loading. They exercise request assembly, format validation, returned identities, usage accounting, a full 100-request fixture run and zero-call resume. The inherited execution tests use the original six-model fixture configuration. The fixtures test runner behavior with simulated responses.

The executable runner, providers, input loader, derivation and scoring are byte copies of v2. Manifests bind the new code, config and input snapshots. Preparation uses local files and requires no credentials.

## Accounting and interpretation

The selected catalog prices per million tokens are GLM $0.15 input, $0.03 cache read and $0.50 output; Kimi $3 input, $0.30 cache read and $15 output. Cache-write rates are unavailable for both endpoints. Response-reported dollars take precedence over estimates. Missing usage or cache information remains null; reasoning tokens are counted once, within the output total. The monetary cap is null.

The full collection still has 20 groups, 40 scientific Choices and one engineering control. Shared code resolves 20 scientific Choices and the control. The recorded source-review subset covers 18 Choices, including 14 model-routed Choices. Model additions and repetitions reuse these same scientific questions. Cross-cohort latency comparisons describe different execution windows. Preparation, human review and complete-workflow costs remain unmeasured.

See [MODEL_SOURCES.md](MODEL_SOURCES.md) and [provider_catalog.json](provider_catalog.json) for route, format, effort and price evidence.
