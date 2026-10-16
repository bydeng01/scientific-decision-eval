# Drag pilot: tokens and latency

This is an offline supplement to the completed diagnostic. No new API calls were made.

The comparison below uses the same four trajectory states for each setting and includes
invalid/incomplete attempts. Empty-prior controls are excluded. The earlier Sonnet
2048-token failure is retained separately and included in cumulative accounting.

| Setting | Valid / attempted | Mean input tokens | Mean output tokens | Mean client seconds | Median seconds | Total charge USD |
|---|---|---:|---:|---:|---:|---:|
| Jev 1.13 / native Choice | 3 / 4 | 1167.50 | 44.00 | 0.469 | 0.354 | 0.000196140 |
| Astra / low / 2048 cap | 4 / 4 | 774.75 | 1514.25 | 46.204 | 51.666 | 0.341587500 |
| Sonnet / low / 8192 cap | 3 / 4 | 1265.75 | 7006.75 | 55.795 | 55.741 | 0.290396000 |

## Accounting across all conditions

The following includes controls, failed requests, and the changed-setting repeat.

| Setting | Calls | Input tokens | Output tokens | Reported reasoning/thinking tokens within output | Sum of client seconds | Charge USD |
|---|---:|---:|---:|---:|---:|---:|
| Jev 1.13 / native Choice | 5 | 5598 | 220 | not reported | 2.326 | 0.000235116 |
| Astra / low / 2048 cap | 5 | 3716 | 6107 | 5886 | 187.925 | 0.351800000 |
| Sonnet / low / 2048 cap | 2 | 2300 | 2101 | 2047 | 19.542 | 0.025610000 |
| Sonnet / low / 8192 cap | 4 | 5063 | 28027 | 27911 | 223.179 | 0.290396000 |

Cumulative charge: USD 0.668041116 across 16 distinct paid requests.

Output tokens already include reported reasoning/thinking tokens. Do not add those
tokens again. Jev does not report an internal reasoning-token breakdown here; this
does not establish zero internal computation. Token counts use each provider's
accounting and do not measure equal computational work across models.

Elapsed time is client-observed request time, including network, gateway, queueing,
and response handling. Jev uses OpenRouter; the baselines use direct provider APIs.
This is not isolated model inference time. The summed request durations exclude gaps
between calls and are not total project wall time. Preprocessing, candidate generation,
and downstream actions were not timed separately in the original pilot.

Four states from two systems do not support stable p95/p99 or throughput estimates.
Quality scores and response failures must accompany speed/cost comparisons; these
measurements do not establish a useful quality-efficiency operating point for Jev.
See ../drag-sonnet-8192-v1/summary.md for quality scores and the retained failures.
