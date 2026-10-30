"""Render the completed three-cohort analysis and error report."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
S = json.loads((HERE / 'summary.json').read_text())
REQUESTS = json.loads((HERE / 'requests.json').read_text())
CHOICES = json.loads((HERE / 'choices.json').read_text())
OUTCOMES = json.loads((HERE / 'outcomes.json').read_text())
ORDER = ['jev', 'luna', 'terra', 'sol', 'astra', 'sonnet', 'qwen_flash', 'qwen_max', 'deepseek_flash', 'deepseek_pro', 'opus5', 'glm_flash', 'kimi_k3']
NAMES = dict(zip(ORDER, ['Jev 1.13', 'GPT-5.6 Luna', 'GPT-5.6 Terra', 'GPT-5.6 Sol', 'GPT-6 Astra', 'Claude Sonnet 5', 'Qwen3.8 Flash', 'Qwen3.8 Max 0902', 'DeepSeek V4.1 Flash', 'DeepSeek V4 Pro 0813', 'Claude Opus 5', 'GLM-5.3-Flash', 'Kimi K3']))
COHORT = {'original': 'A', 'extension': 'B', 'glm_kimi': 'C'}


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] + ['| ' + ' | '.join(map(str, row)) + ' |' for row in rows])


def fraction(value):
    return f"{value['correct']}/{value['denominator']}"


def latency(value):
    return f"{value['median']:.3f} / {value['p95_nearest_rank']:.3f}" if value['median'] is not None else 'unknown'


def tokens(value):
    n = value['known_subtotal']
    return f'{n:,}' if n is not None else 'unreported'


def write(name, value):
    p = HERE / name
    if p.exists():
        assert p.read_text() == value, f'Changed report: use a new directory ({name})'
    else:
        with p.open('x') as f:
            f.write(value)


quality, repeats, timing, resources, execution = [], [], [], [], []
for mid in ORDER:
    m = S['models'][mid]
    quality.append([NAMES[mid], COHORT[m['cohort']], fraction(m['semantic_fixed']), fraction(m['semantic_observed_secondary']), fraction(m['model_dependent_outcomes_exact']), fraction(m['model_dependent_labels_exact']), m['choice_categories'].get('semantic_error', 0), m['failed_requests']])
    repeats.append([NAMES[mid], *[r['semantic_fixed']['correct'] for r in m['per_repeat']], m['all_five_correct_questions']])
    timing.append([NAMES[mid], COHORT[m['cohort']], m['successful_requests'], latency(m['latency_successful']), latency(m['latency_all_terminal']), f"{m['cost']['known_cost_per_successful_request']:.8f}"])
    r, c = m['resources'], m['cost']
    resources.append([NAMES[mid], m['successful_requests'], *[tokens(r[k]) for k in ('input_tokens', 'output_tokens', 'cached_input_tokens', 'cache_write_tokens', 'reasoning_or_thinking_tokens')], f"{c['selected_reported_else_estimated']['known_subtotal']:.9f}", 'reported' if c['server_reported']['known_records'] else 'estimated'])
for key in ('original', 'extension', 'glm_kimi'):
    e = S['cohorts'][key]['execution']
    execution.append([COHORT[key], e['planned'], e['predictions'], e['http_status_counts'].get('200', 0), e['http_status_counts'].get('429', 0), e['http_status_counts'].get('None', 0), e['first_intent_at'], e['last_receipt_at']])

report = '''# S2: thirteen-model development analysis

Kimi adds a sixth model with 100/100 correct planned semantic answers. GLM has 41 HTTP 429 responses out of 50 attempts: its 18/100 fixed-denominator score records 18 correct received answers and 82 answers absent because of those operational failures.

Jev retains the lowest observed successful-request median latency and known per-success cost with perfect coverage. All cohorts use the same development questions.

## Completion and integrity

''' + table(['Cohort', 'Planned', 'Terminal', 'HTTP 200', 'HTTP 429', 'Uncertain', 'First intent UTC', 'Last receipt UTC'], execution) + '''

A contains the original six models, B the five-model extension, and C GLM and Kimi. All 650 planned requests have terminal records. The final GLM/Kimi report was generated at 2026-09-21 08:21:55 UTC. There were no retries or fallbacks. Terra's original interruption remains an unknown server outcome. The 52 received rate-limit responses remain operational failures. All 597 HTTP 200 responses satisfy the existing format and model/provider contracts; there are zero format errors and zero missing answer fields within these successful responses.

The original archive audit verified all manifests, reparsed 650 saved receipts, matched 1,950 attempt-file hashes, and reproduced all 13 historical model score objects. Inputs, reference answers, packets and question maps agree across all cohorts. The shared dataset, derivation and scoring code is byte-identical. Code outputs and the reference oracle were regenerated, and 356 expected-null fields were preserved in received model-dependent derivations. The original manifests record no Git HEAD because the runs were prepared outside a Git checkout; saved snapshots and hashes identify the versions.

The 2026-09-21 audit checked 2,390 protected files, including the eleven-model analysis and the 1,994-file pre-GLM/Kimi baseline. Those hashes identify the original archive. Current published-file hashes and verification instructions are in [RELEASE.md](../../RELEASE.md). Integrity and scoring checks do not constitute a new scientific source audit.

## Choice and derived-outcome scores

The collection contains 20 groups, 40 scientific Choices and one engineering control. Code resolves 20 scientific Choices plus the control. Models answer the other 20 Choices in 10 groups. Each model has five repetitions: 100 planned semantic answers and 50 model-dependent outcomes. The primary fixed denominators include absent answers; the observed-answer score is secondary and can have selective coverage. Code-only and oracle results are reported separately from model scores.

''' + table(['Model', 'Cohort', 'Choice /100', 'Observed Choice', 'Full derived /50', 'Labels /50', 'Semantic errors', 'Failed requests'], quality) + '''

Across the recorded workload, 1,187/1,300 planned semantic answers are correct, 7 are wrong, and 106 are absent. Of the 650 model-dependent outcomes, 590 match the full reference and 597 match its final label. These totals aggregate repeated calls to the same scientific questions. All seven known semantic errors remain on B002-Q01: Luna R2, Qwen Flash R1, and Qwen Max R1–R5. Each changes culture-history counts while leaving the final label unchanged. No additional semantic error appears in the two new models. Counts-only exactness equals full-outcome exactness for every model.

Kimi achieves 100/100 semantic, 50/50 full derived and 50/50 label scores. GLM achieves 18/18 received semantic answers and 9/9 received full outcomes. Its fixed scores are 18/100 and 9/50 because of the 41 rate limits. Received-answer scores cover the nine successful requests; performance on the unanswered requests remains unknown.

## Five-repeat stability

Each repeat has a denominator of 20 semantic answers. The last column counts unique Choices received and correct in all five repeats.

''' + table(['Model', 'R1 /20', 'R2 /20', 'R3 /20', 'R4 /20', 'R5 /20', 'All five correct /20'], repeats) + '''

GLM provides no valid answers in repeats 3–5, so its five-repeat semantic stability is unmeasured. Kimi returns the reference answer for all 20 Choices in every repeat. The only variability between valid answer options remains B002-Q01 for Luna, Qwen Flash and Qwen Max. Qwen Max returns three different wrong options across its five attempts.

The recorded source-review subset covers 18 Choices, including 14 of the 20 model-routed Choices. E004-Q01/Q02, E005-Q01/Q02 and E009-Q01/Q02 are outside that review subset. Their references remain the existing development references; this audit neither rejects nor independently validates them. Per-Choice answers, errors and review flags are in [choices.json](choices.json); full output comparisons are in [outcomes.json](outcomes.json).

## Tokens, cache and cost

Values below are known subtotals over saved successful responses. A row with fewer than 50 responses has incomplete usage coverage, including when an observed subtotal is zero. Missing fields remain null. Reasoning/thinking tokens are counted once, within output tokens. OpenAI and router input totals include cache quantities; Anthropic ordinary input is reported separately.

''' + table(['Model', 'Usage n', 'Input', 'Output', 'Cache read', 'Cache write', 'Reasoning/thinking', 'Known USD', 'Basis'], resources) + '''

Cohort C adds $0.274938350 in server-reported charges: $0.001625150 for GLM's nine successes and $0.273313200 for Kimi's 50 successes. The combined known subtotal is $2.087270962, comprising $0.721179462 reported for 298 responses and $1.366091500 estimated from usage for 299 other responses. Total cost for all 650 attempts remains unknown because 53 operational exceptions have no saved usage/charge. Charges for HTTP 429 responses remain unknown, and the subtotal has not been reconciled against invoices. Usage estimates cross-check reported costs and enter the subtotal only when a response has no reported charge.

The original six-model cost reconciliation remains unchanged. This analysis includes the raw cache-write and thinking fields omitted by the original normalizer. Prices come from saved execution configurations. Kimi reports 41,984 cached input tokens out of 60,450 prompt tokens and 12,347 reasoning tokens out of 13,688 output tokens; GLM reports zero cache reads over its nine received responses. Cache use varies across workloads, and internal compute is unmatched.

## Latency

Latency is the saved client request interval. The primary column includes successes; the secondary column includes all known terminal intervals. p95 uses nearest rank. All three cohorts were executed in separate time windows. GLM's success p95 uses only nine responses and equals its largest observed success interval.

''' + table(['Model', 'Cohort', 'Success n', 'Success median / p95 s', 'All known median / p95 s', 'Known USD / success'], timing) + '''

GLM's short 429 responses reduce its all-terminal median to 0.534 seconds, compared with 1.821 seconds for successes. Kimi's successful median/p95 is 11.116/25.744 seconds. Jev retains the lowest observed success median (0.335 seconds) and known cost per successful request ($0.000059535). These measurements describe the recorded routes, settings, cache use and separate execution windows. Comparisons are specific to these runs.

## Reproduction

From the repository root:

```bash
python3 -B scripts/verify_release.py
```

The release verifier checks published-file hashes, reparses the saved responses, and reproduces all thirteen model score objects without modifying results. The historical `verify_analysis.py` requires the original private archive. Changed source data require a new analysis directory. [summary.json](summary.json) holds aggregate results; [requests.json](requests.json) holds response-level resources and hashes; [ERRORS.md](ERRORS.md) lists exceptions; `audit-*.json` and `rescored-*.json` hold cohort audit evidence and reproduced scores. [verification.json](verification.json) records the original archive reproduction checks.
'''
write('REPORT.md', report)

semantic = [c for c in CHOICES if c['category'] == 'semantic_error']
errors = []
for c in semantic:
    o = next(o for o in OUTCOMES if o['job_id'] == c['job_id'])
    req = next(r for r in REQUESTS if r['job_id'] == c['job_id'])
    errors.append([f"[{c['job_id']}](../../{req['receipt_path']})", c['question_id'], c['reference'], c['prediction'], o['exact'], o['label_exact']])
failed = []
for r in REQUESTS:
    if r['status'] != 'complete':
        failed.append([f"[{r['job_id']}](../../{r['receipt_path']})", r['http_status'] if r['http_status'] is not None else 'unknown', r['transport_error'] or r['limit_source'] or '; '.join(sorted(set(r['errors'].values()))), 'unknown'])
write('ERRORS.md', '''# S2 semantic and operational exceptions

All seven known semantic errors concern B002-Q01. The reference `shared_then_separate` maps culture growth histories to 11a:1 and 11:10. The wrong answers change these counts; B002-Q02 remains `clonal_descendants`, mutation origins remain null, colony totals remain 514 and 624, and the final label remains inconsistent. These are seven responses to one unique scientific Choice.

''' + table(['Attempt', 'Choice', 'Reference', 'Prediction', 'Full output exact', 'Label exact'], errors) + '''

The following 53 operational exceptions account for 106 absent semantic answers. Terra's interruption has unknown server completion. The other 52 records are received HTTP 429s, including 41 GLM/Fireworks failures. No absent answer is classified as a semantic mistake or converted into `not_stated`. Saved rate-limit metadata describes the service response; it is not an independent upstream diagnosis. Costs remain unknown.

''' + table(['Attempt', 'HTTP', 'Saved error or limit source', 'Cost'], failed) + '\n\nThere are no format/contract errors or missing answer fields in the 597 HTTP 200 responses. Complete actual/reference projections are in [outcomes.json](outcomes.json).\n')
