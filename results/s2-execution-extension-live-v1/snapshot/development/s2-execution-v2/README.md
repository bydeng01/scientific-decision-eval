# S2 model extension

This version adds five models to the original six-model evaluation. It runs the same development evidence, options, code routes and scoring as v1. The original six models and their recorded results remain in `results/s2-execution-live-v1`. Together, the two cohorts cover eleven models.

The added matrix is 10 model-routed groups × 5 models × 5 repetitions: 250 requests and 500 semantic answers. Each model has a fixed denominator of 100 semantic Choices and 50 model-dependent derived outcomes. Code-only and reference-oracle checks remain separate. All 20 groups, 40 scientific Choices and the engineering control retain their current mapping; the recorded 18-Choice source-review subset remains a subset.

| Local ID | Requested model | Interface and fixed upstream | Reasoning setting |
|---|---|---|---|
| qwen_flash | qwen/qwen3.8-flash | OpenRouter Chat → Alibaba | medium |
| qwen_max | qwen/qwen3.8-max-0902 | OpenRouter Chat → Alibaba | medium |
| deepseek_flash | deepseek/deepseek-v4.1-flash | OpenRouter Chat → Fireworks | high |
| deepseek_pro | deepseek/deepseek-v4-pro-0813 | OpenRouter Chat → Fireworks | high |
| opus5 | claude-opus-5 | Anthropic Messages | adaptive, medium |

Supply OpenRouter and Anthropic credentials through environment variables or the local credential helper. The runner never prints keys or writes authorization headers into results. OpenRouter's `only`, `allow_fallbacks: false` and `require_parameters: true` restrict each request to the configured service and supported parameters. Returned model IDs and provider names are checked; a mismatch halts that model.

`provider_catalog.json` preserves the unauthenticated endpoint listing and retrieval time. Fireworks supports both selected DeepSeek snapshots, JSON schema and the existing 32,768-token output envelope. The inspected DeepInfra Pro endpoint supports only 16,384 completion tokens, so it was not selected. Upstream quantization is recorded as unknown where the catalog does not specify it. Model and route names do not establish immutable weight hashes.

DeepSeek's ordinary documented thinking setting is `high`; its first-party API maps the compatibility value `medium` to `high`. We request `high` explicitly through OpenRouter. Qwen requests `medium` through the router, and Opus uses the same adaptive-medium condition as the earlier Sonnet run. These settings specify requested interface behavior; internal computation is not matched across services.

The five repetitions, serial concurrency, 300-second total deadline, zero retries and zero fallbacks are inherited from v1. The output envelope remains 32,768 tokens including reasoning. The budget policy has no monetary cap. Failures and ambiguous interruptions remain in the planned denominator and are not replaced.

## Commands

Run from the repository root with Python 3.10 or later:

```bash
# Offline checks, including the inherited behavior and added provider contracts.
python3 -B development/s2-execution-v2/run.py check

# New directory required; simulated responses only.
python3 -B development/s2-execution-v2/run.py dry-run --output results/s2-execution-extension-dry-next

# Prepare a new execution directory without making calls.
python3 -B development/s2-execution-v2/run.py prepare --output results/s2-execution-extension-new

# Real calls; repeating this command resumes without replacing completed attempts.
python3 -B development/s2-execution-v2/run.py run --output results/s2-execution-extension-new --live

# Offline verification and rescoring.
python3 -B development/s2-execution-v2/run.py verify --output results/s2-execution-extension-new
python3 -B development/s2-execution-v2/run.py score --output results/s2-execution-extension-new
```

Verify the distributed historical results with `python3 -B scripts/verify_release.py`. The commands above use a new directory prepared from the current source files.

The runner prints a request-start and request-finish event, including job ID, status and latency. `--limit N` bounds new attempts in one invocation without changing the planned matrix. The first five scheduled requests include one request from every added model and remain ordinary scored attempts.

## Accounting and preservation

V2 normalizes OpenRouter Chat's `prompt_tokens`, `completion_tokens` and their detail objects. It also recognizes OpenAI's `cache_write_tokens` and Claude's `thinking_tokens`, which were present in the first run's raw responses but omitted by its normalizer. Reasoning tokens are counted once, within output totals. Missing usage remains null. Provider-reported charges, token-price estimates and conservative upper estimates stay separate.

The input loader, derivation and scoring files are byte copies of v1. `regression_config.json` supplies the original six-model fixtures to the inherited offline tests; the live default `config.json` contains only the five additions. Preparation snapshots all v2 source files, including the catalog and this document.

The extension is a later cohort using identical development packets and references. Latency and cost comparisons describe the recorded service load, cache state and execution times. Unseen-source performance remains unmeasured.
